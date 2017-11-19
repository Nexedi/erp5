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

// Import
var g_oTableId = AscCommon.g_oTableId;
var History = AscCommon.History;

var c_oAscHAnchor = Asc.c_oAscHAnchor;
var c_oAscXAlign = Asc.c_oAscXAlign;
var c_oAscYAlign = Asc.c_oAscYAlign;
var c_oAscVAnchor = Asc.c_oAscVAnchor;


/**
 * Класс CDocumentContent. Данный класс используется для работы с контентом ячеек таблицы, колонтитулов, сносок,
 * надписей.
 * @param Parent
 * @param DrawingDocument
 * @param X
 * @param Y
 * @param XLimit
 * @param YLimit
 * @param Split
 * @param TurnOffInnerWrap
 * @param bPresentation
 * @constructor
 * @extends {CDocumentContentBase}
 */
function CDocumentContent(Parent, DrawingDocument, X, Y, XLimit, YLimit, Split, TurnOffInnerWrap, bPresentation)
{
	CDocumentContentBase.call(this);

    this.Id = AscCommon.g_oIdCounter.Get_NewId();

    this.X = X;
    this.Y = Y;
    this.XLimit = XLimit;
    this.YLimit = YLimit;

	this.StartPage    = 0;
	this.StartColumn  = 0;
	this.ColumnsCount = 1;

    this.Parent = Parent;
    
    this.DrawingDocument = null;
    this.LogicDocument   = null;
    this.Styles          = null;
    this.Numbering       = null;
    this.DrawingObjects  = null;
    
    if ( undefined !== DrawingDocument && null !== DrawingDocument )
    {
        this.DrawingDocument = DrawingDocument;
        
        if ( undefined !== editor && true === editor.isDocumentEditor && !(bPresentation === true) && DrawingDocument.m_oLogicDocument )
        {
            this.LogicDocument   = DrawingDocument.m_oLogicDocument;
            this.Styles          = DrawingDocument.m_oLogicDocument.Get_Styles();
            this.Numbering       = DrawingDocument.m_oLogicDocument.Get_Numbering();
            this.DrawingObjects  = DrawingDocument.m_oLogicDocument.DrawingObjects; // Массив укзателей на все инлайновые графические объекты
        }
    }

    if ( "undefined" === typeof(TurnOffInnerWrap) )
        TurnOffInnerWrap = false;

    this.TurnOffInnerWrap = TurnOffInnerWrap;

    this.Pages = [];

    this.RecalcInfo = new CDocumentRecalcInfo();

    this.Split = Split; // Разделяем ли на страницы
    this.bPresentation = bPresentation; // Разделяем ли на страницы

    this.Content[0] = new Paragraph( DrawingDocument, this, bPresentation );
    this.Content[0].Correct_Content();
    this.Content[0].Set_DocumentNext( null );
    this.Content[0].Set_DocumentPrev( null );

    this.CurPos  =
    {
        X          : 0,
        Y          : 0,
        ContentPos : 0, // в зависимости, от параметра Type: позиция в Document.Content
        RealX      : 0, // позиция курсора, без учета расположения букв
        RealY      : 0, // это актуально для клавиш вверх и вниз
        Type       : docpostype_Content,
        TableMove  : 0  // специльный параметр для переноса таблиц
    };

    this.Selection =
    {
        Start    : false,
        Use      : false,
        StartPos : 0,
        EndPos   : 0,
        Flag     : selectionflag_Common,
        Data     : null
    };

    this.ClipInfo = [];

    this.ApplyToAll = false; // Специальный параметр, используемый в ячейках таблицы.
                             // True, если ячейка попадает в выделение по ячейкам.

    this.TurnOffRecalc = false;

    this.m_oContentChanges = new AscCommon.CContentChanges(); // список изменений(добавление/удаление элементов)
    this.StartState = null;

    this.ReindexStartPos = 0;

    // Добавляем данный класс в таблицу Id (обязательно в конце конструктора)
    g_oTableId.Add( this, this.Id );

    if(this.bPresentation)
    {
        this.Save_StartState();
    }
}
CDocumentContent.prototype = Object.create(CDocumentContentBase.prototype);
CDocumentContent.prototype.constructor = CDocumentContent;

CDocumentContent.prototype.Save_StartState = function()
{
    this.StartState = new CDocumentContentStartState(this);
};
CDocumentContent.prototype.Copy = function(Parent, DrawingDocument)
{
	var DC = new CDocumentContent(Parent, DrawingDocument ? DrawingDocument : this.DrawingDocument, 0, 0, 0, 0, this.Split, this.TurnOffInnerWrap, this.bPresentation);

	// Копируем содержимое
	DC.Internal_Content_RemoveAll();

	var Count = this.Content.length;
	for (var Index = 0; Index < Count; Index++)
	{
		DC.Internal_Content_Add(Index, this.Content[Index].Copy(DC, DrawingDocument), false);
	}

	return DC;
};
CDocumentContent.prototype.Copy2 = function(OtherDC)
{
	// Копируем содержимое
	this.Internal_Content_RemoveAll();

	var Count = OtherDC.Content.length;
	for (var Index = 0; Index < Count; Index++)
	{
		this.Internal_Content_Add(Index, OtherDC.Content[Index].Copy(this), false);
	}
};
CDocumentContent.prototype.Copy3 = function(Parent)//для заголовков диаграмм
{
	var DC = new CDocumentContent(Parent, this.DrawingDocument, 0, 0, 0, 0, this.Split, this.TurnOffInnerWrap, true);

	// Копируем содержимое
	DC.Internal_Content_RemoveAll();

	var Count = this.Content.length;
	for (var Index = 0; Index < Count; Index++)
	{
		DC.Internal_Content_Add(Index, this.Content[Index].Copy2(DC), false);
	}
	return DC;
};
//-----------------------------------------------------------------------------------
// Функции, к которым идет обращение из контента
//-----------------------------------------------------------------------------------
CDocumentContent.prototype.Get_PageContentStartPos = function(PageNum)
{
	return this.Parent.Get_PageContentStartPos(PageNum);
};
CDocumentContent.prototype.Get_PageContentStartPos2 = function(StartPageIndex, StartColumnIndex, ElementPageIndex, ElementIndex)
{
    return this.Get_PageContentStartPos(StartPageIndex + ElementPageIndex);
};
CDocumentContent.prototype.Get_Theme = function()
{
	if(this.Parent){
        return this.Parent.Get_Theme();
	}
	return null;
};
CDocumentContent.prototype.Get_ColorMap = function()
{
	if(this.Parent){
        return this.Parent.Get_ColorMap();
	}
	return null;
};
CDocumentContent.prototype.Get_PageLimits = function(PageIndex)
{
	if (true === this.Parent.IsCell())
	{
		var Margins = this.Parent.GetMargins();

		var Y      = this.Pages[PageIndex].Y - Margins.Top.W;
		var YLimit = this.Pages[PageIndex].YLimit + Margins.Bottom.W;
		var X      = this.Pages[PageIndex].X - Margins.Left.W;
		var XLimit = this.Pages[PageIndex].XLimit + Margins.Right.W;

		return {X : X, XLimit : XLimit, Y : Y, YLimit : YLimit}
	}
	else
	{
		if (null === this.LogicDocument)
			return {X : 0, Y : 0, XLimit : 0, YLimit : 0};

		var Page_abs = this.Get_StartPage_Absolute() + PageIndex;
		var Index    = ( undefined !== this.LogicDocument.Pages[Page_abs] ? this.LogicDocument.Pages[Page_abs].Pos : 0 );
		var SectPr   = this.LogicDocument.SectionsInfo.Get_SectPr(Index).SectPr;
		var Orient   = SectPr.Get_Orientation();

		var W = SectPr.Get_PageWidth();
		var H = SectPr.Get_PageHeight();

		return {X : 0, Y : 0, XLimit : W, YLimit : H};
	}
};
CDocumentContent.prototype.Get_PageFields = function(PageIndex)
{
	if (true === this.Parent.IsCell() || (undefined !== AscFormat.CShape && this.Parent instanceof AscFormat.CShape))
	{
		if (PageIndex < this.Pages.length && PageIndex >= 0)
		{
			var Y      = this.Pages[PageIndex].Y;
			var YLimit = this.Pages[PageIndex].YLimit;
			var X      = this.Pages[PageIndex].X;
			var XLimit = this.Pages[PageIndex].XLimit;

			return {X : X, XLimit : XLimit, Y : Y, YLimit : YLimit}
		}
		else
		{
			if (null === this.LogicDocument)
				return {X : 0, Y : 0, XLimit : 0, YLimit : 0};

			var Page_abs = this.Get_AbsolutePage(PageIndex);
			var Index    = ( undefined !== this.LogicDocument.Pages[Page_abs] ? this.LogicDocument.Pages[Page_abs].Pos : 0 );
			var SectPr   = this.LogicDocument.SectionsInfo.Get_SectPr(Index).SectPr;
			var Orient   = SectPr.Get_Orientation();

			var W = SectPr.Get_PageWidth();
			var H = SectPr.Get_PageHeight();

			return {X : 0, Y : 0, XLimit : W, YLimit : H};
		}
	}
	else
	{
		if (null === this.LogicDocument)
			return {X : 0, Y : 0, XLimit : 0, YLimit : 0};

		var Page_abs = this.Get_AbsolutePage(PageIndex);
		var Index    = ( undefined !== this.LogicDocument.Pages[Page_abs] ? this.LogicDocument.Pages[Page_abs].Pos : 0 );
		var SectPr   = this.LogicDocument.SectionsInfo.Get_SectPr(Index).SectPr;
		var Orient   = SectPr.Get_Orientation();

		var Y      = SectPr.PageMargins.Top;
		var YLimit = SectPr.PageSize.H - SectPr.PageMargins.Bottom;
		var X      = SectPr.PageMargins.Left;
		var XLimit = SectPr.PageSize.W - SectPr.PageMargins.Right;

		return {X : X, Y : Y, XLimit : XLimit, YLimit : YLimit};
	}

};
CDocumentContent.prototype.Get_EmptyHeight = function()
{
	var Count = this.Content.length;
	if (Count <= 0)
		return 0;

	var Element = this.Content[Count - 1];

	if (type_Paragraph === Element.GetType())
		return Element.Get_EmptyHeight();
	else
		return 0;
};
/**
 * Inner = true  - запрос пришел из содержимого,
 *         false - запрос пришел от родительского класса
 *         Запрос от родительского класса нужен, например, для колонтитулов, потому
 *         что у них врапится текст не колонтитула, а документа.
 */
CDocumentContent.prototype.CheckRange = function(X0, Y0, X1, Y1, _Y0, _Y1, X_lf, X_rf, CurPage, Inner, bMathWrap)
{
	if (undefined === Inner)
		Inner = true;

	if (this.IsBlockLevelSdtContent() && true === Inner)
		return this.Parent.CheckRange(X0, Y0, X1, Y1, _Y0, _Y1, X_lf, X_rf, CurPage, true, bMathWrap);

	if (this.LogicDocument && editor && editor.isDocumentEditor)
	{
		var oDocContent = this;
		if (this.Parent && this.Parent instanceof CBlockLevelSdt)
			oDocContent = this.Parent.Parent;

		if ((false === this.TurnOffInnerWrap && true === Inner) || (false === Inner))
			return this.LogicDocument.DrawingObjects.CheckRange(X0, Y0, X1, Y1, _Y0, _Y1, X_lf, X_rf, this.Get_AbsolutePage(CurPage), [], this, bMathWrap);
	}

	return [];
};
CDocumentContent.prototype.Is_PointInDrawingObjects = function(X, Y, Page_Abs)
{
	return this.LogicDocument && this.LogicDocument.DrawingObjects.pointInObjInDocContent(this, X, Y, Page_Abs);
};
CDocumentContent.prototype.Is_PointInFlowTable = function(X, Y, PageAbs)
{
	return this.LogicDocument && null !== this.LogicDocument.DrawingObjects.getTableByXY(X, Y, PageAbs, this);
};
CDocumentContent.prototype.Get_Numbering = function()
{
	return this.Parent.Get_Numbering();
};
CDocumentContent.prototype.Internal_GetNumInfo = function(ParaId, NumPr)
{
	var TopDocument = this.Get_TopDocumentContent();
	if (TopDocument instanceof CFootEndnote)
		return TopDocument.Parent.GetNumberingInfo(ParaId, NumPr, TopDocument);

	return TopDocument.GetNumberingInfo(null, ParaId, NumPr);
};
CDocumentContent.prototype.Get_Styles = function(lvl)
{
	if (this.Content[0] && this.Content[0].bFromDocument)
		return this.Styles;
	else
		return this.Parent.Get_Styles(lvl);
};
CDocumentContent.prototype.Get_TableStyleForPara = function()
{
	return this.Parent.Get_TableStyleForPara();
};
CDocumentContent.prototype.Get_ShapeStyleForPara = function()
{
	return this.Parent.Get_ShapeStyleForPara();
};
CDocumentContent.prototype.Get_TextBackGroundColor = function()
{
	return this.Parent.Get_TextBackGroundColor();
};
CDocumentContent.prototype.Recalc_AllParagraphs_CompiledPr = function()
{
	var Count = this.Content.length;
	for (var Pos = 0; Pos < Count; Pos++)
	{
		var Item = this.Content[Pos];
		if (type_Paragraph === Item.GetType())
		{
			Item.Recalc_CompiledPr();
			Item.Recalc_RunsCompiledPr();
		}
		else if (type_Table === Item.GetType())
			Item.Recalc_CompiledPr2();
	}
};
CDocumentContent.prototype.Set_CurrentElement = function(Index, bUpdateStates)
{
	var ContentPos = Math.max(0, Math.min(this.Content.length - 1, Index));
	this.Set_DocPosType(docpostype_Content);

	var CurPos = Math.max(0, Math.min(this.Content.length - 1, Index));

	this.Selection.Use      = false;
	this.Selection.Start    = false;
	this.Selection.Flag     = selectionflag_Common;
	this.Selection.StartPos = CurPos;
	this.Selection.EndPos   = CurPos;
	this.CurPos.ContentPos  = CurPos;

	if (true === this.Content[ContentPos].IsSelectionUse())
	{
		this.Selection.Use      = true;
		this.Selection.StartPos = ContentPos;
		this.Selection.EndPos   = ContentPos;
	}

	this.Parent.Set_CurrentElement(bUpdateStates, this.Get_StartPage_Absolute(), this);
};
CDocumentContent.prototype.Is_ThisElementCurrent = function()
{
	return this.Parent.Is_ThisElementCurrent(this);
};
// Получем ближающую возможную позицию курсора
CDocumentContent.prototype.Get_NearestPos = function(CurPage, X, Y, bAnchor, Drawing)
{
	// TODO: Возможно лучше вернуть null, и разобраться с ситуациями, когда Get_NearestPos возвращает null
	if (CurPage < 0)
	{
		Y       = 0;
		CurPage = 0;
	}
	else if (CurPage >= this.Pages.length)
	{
		CurPage = this.Pages.length - 1;
		Y       = 10000;
	}

	var PageAbs = this.Get_AbsolutePage(CurPage);

	if (this.Parent && this.Parent instanceof CHeaderFooter)
	{
		var bInText    = (null === this.IsInText(X, Y, CurPage) ? false : true);
		var nInDrawing = this.LogicDocument.DrawingObjects.IsInDrawingObject(X, Y, PageAbs, this);

		if (true != bAnchor)
		{
			// Проверяем попадание в графические объекты
			var NearestPos = this.LogicDocument.DrawingObjects.getNearestPos(X, Y, PageAbs, Drawing);
			if (( nInDrawing === DRAWING_ARRAY_TYPE_BEFORE || nInDrawing === DRAWING_ARRAY_TYPE_INLINE || ( false === bInText && nInDrawing >= 0 ) ) && null != NearestPos)
				return NearestPos;
		}
	}

	var ContentPos = this.Internal_GetContentPosByXY(X, Y, CurPage);

	// Делаем логику как в ворде
	if (true != bAnchor && (0 < ContentPos || CurPage > 0) && ContentPos === this.Pages[CurPage].Pos && this.Pages[CurPage].EndPos > this.Pages[CurPage].Pos && type_Paragraph === this.Content[ContentPos].GetType() && true === this.Content[ContentPos].IsContentOnFirstPage())
		ContentPos++;

	var ElementPageIndex = this.private_GetElementPageIndexByXY(ContentPos, X, Y, CurPage);
	return this.Content[ContentPos].Get_NearestPos(ElementPageIndex, X, Y, bAnchor, Drawing);
};
// Проверяем, описывает ли данный класс содержимое ячейки
CDocumentContent.prototype.IsTableCellContent = function(isReturnCell)
{
	return this.Parent.IsCell(isReturnCell);
};
CDocumentContent.prototype.IsTableFirstRowOnNewPage = function()
{
	if (false === this.Parent.IsCell())
		return false;

	return this.Parent.IsTableFirstRowOnNewPage();
};
CDocumentContent.prototype.Check_AutoFit = function()
{
	return this.Parent.Check_AutoFit();
};
// Проверяем, лежит ли данный класс в таблице
CDocumentContent.prototype.Is_InTable = function(bReturnTopTable)
{
	return this.Parent.Is_InTable(bReturnTopTable);
};
// Проверяем, является ли данный класс верхним, по отношению к другим классам DocumentContent, Document
CDocumentContent.prototype.Is_TopDocument = function(bReturnTopDocument)
{
	return this.Parent.Is_TopDocument(bReturnTopDocument);
};
// Проверяем, используется ли данный элемент в документе
CDocumentContent.prototype.Is_UseInDocument = function(Id)
{
	var bUse = false;

	if (null != Id)
	{
		var Count = this.Content.length;
		for (var Index = 0; Index < Count; Index++)
		{
			if (Id === this.Content[Index].Get_Id())
			{
				bUse = true;
				break;
			}
		}
	}
	else
		bUse = true;

	if (true === bUse && null != this.Parent)
		return this.Parent.Is_UseInDocument(this.Get_Id());

	return false;
};
CDocumentContent.prototype.Is_HdrFtr = function(bReturnHdrFtr)
{
	if (this.Parent)
		return this.Parent.Is_HdrFtr(bReturnHdrFtr);
	else
		return (bReturnHdrFtr ? null : false);
};
CDocumentContent.prototype.Is_DrawingShape = function(bRetShape)
{
	if (this.Parent)
		return this.Parent.Is_DrawingShape(bRetShape);
	else
		return (bRetShape ? null : false);
};
CDocumentContent.prototype.IsMovingTableBorder = function()
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.DrawingObjects.selectionIsTableBorder();
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (null != this.Selection.Data && true === this.Selection.Data.TableBorder)
			return true;
	}

	return false;
};
CDocumentContent.prototype.CheckTableCoincidence = function(Table)
{
	return this.Parent.CheckTableCoincidence(Table);
};
//-----------------------------------------------------------------------------------
// Основные функции, к которым идет обращение от родительского класса
//-----------------------------------------------------------------------------------
CDocumentContent.prototype.Reset = function(X, Y, XLimit, YLimit)
{
	this.X      = X;
	this.Y      = Y;
	this.XLimit = XLimit;
	this.YLimit = YLimit;

	// Заглушка для работы курсора в новой таблице
	if (0 === this.CurPos.X && 0 === this.CurPos.Y)
	{
		this.CurPos.X = X;
		this.CurPos.Y = Y;

		this.CurPos.RealX = X;
		this.CurPos.RealY = Y;
	}

	this.ClipInfo = [];
};
CDocumentContent.prototype.Recalculate                    = function()
{
    if (typeof(editor) !== "undefined" && editor.isDocumentEditor)
    {
        editor.WordControl.m_oLogicDocument.bRecalcDocContent    = true;
        editor.WordControl.m_oLogicDocument.recalcDocumentConten = this;
        editor.WordControl.m_oLogicDocument.Recalculate();
    }
};
CDocumentContent.prototype.Reset_RecalculateCache = function()
{
	var Count = this.Content.length;
	for (var Index = 0; Index < Count; Index++)
	{
		this.Content[Index].Reset_RecalculateCache();
	}
};
// Пересчитываем отдельную страницу DocumentContent
CDocumentContent.prototype.Recalculate_Page               = function(PageIndex, bStart)
{
    if (0 === PageIndex && true === bStart && true !== this.IsBlockLevelSdtContent())
    {
        this.RecalcInfo.FlowObject                = null;
        this.RecalcInfo.FlowObjectPageBreakBefore = false;
    }

    var StartIndex = 0;
    if (PageIndex > 0)
        StartIndex = this.Pages[PageIndex - 1].EndPos;

    if (true === bStart)
    {
        this.Pages.length         = PageIndex;
        this.Pages[PageIndex]     = new CDocumentPage();
        this.Pages[PageIndex].Pos = StartIndex;
        if (this.LogicDocument)
            this.LogicDocument.DrawingObjects.resetDrawingArrays(this.Get_AbsolutePage(PageIndex), this);
    }

    var Count = this.Content.length;

    var StartPos;
    if (0 === PageIndex)
    {
        StartPos = {
            X      : this.X,
            Y      : this.Y,
            XLimit : this.XLimit,
            YLimit : this.YLimit
        }
    }
    else
    {
		StartPos = this.Get_PageContentStartPos(PageIndex);
    }

    this.Pages[PageIndex].Update_Limits(StartPos);

    var X      = StartPos.X;
    var StartY = StartPos.Y;
    var Y      = StartY;
    var YLimit = StartPos.YLimit;
    var XLimit = StartPos.XLimit;

    var Result = recalcresult2_End;

    for (var Index = StartIndex; Index < Count; Index++)
    {
        // Пересчитываем элемент документа
        var Element = this.Content[Index];

        var RecalcResult = recalcresult_NextElement;
        var bFlow        = false;
        if (type_Table === Element.GetType() && true != Element.Is_Inline())
        {
            bFlow = true;
            if (true === this.RecalcInfo.Can_RecalcObject())
            {
                Element.Set_DocumentIndex(Index);
                Element.Reset(X, Y, XLimit, YLimit, PageIndex, 0, 1);
                var TempRecalcResult = Element.Recalculate_Page(0);
                this.RecalcInfo.Set_FlowObject(Element, 0, TempRecalcResult, -1, {
                    X      : X,
                    Y      : Y,
                    XLimit : XLimit,
                    YLimit : YLimit
                });

                if (this.DrawingObjects)
                    this.DrawingObjects.addFloatTable(new CFlowTable(Element, PageIndex));

                RecalcResult = recalcresult_CurPage;
            }
            else if (true === this.RecalcInfo.Check_FlowObject(Element))
            {
                // Если у нас текущая страница совпадает с той, которая указана в таблице, тогда пересчитываем дальше
                if (Element.PageNum > PageIndex || ( this.RecalcInfo.FlowObjectPage <= 0 && Element.PageNum < PageIndex ) || Element.PageNum === PageIndex)
                {
                    if (true === this.RecalcInfo.FlowObjectPageBreakBefore)
                    {
                        // Добавляем начало таблицы в конец страницы так, чтобы не убралось ничего
                        Element.Set_DocumentIndex(Index);
                        Element.Reset(X, YLimit, XLimit, YLimit, PageIndex, 0, 1);
                        Element.Recalculate_Page(0);

                        this.RecalcInfo.FlowObjectPage++;
                        RecalcResult = recalcresult_NextPage;
                    }
                    else
                    {
                        X      = this.RecalcInfo.AdditionalInfo.X;
                        Y      = this.RecalcInfo.AdditionalInfo.Y;
                        XLimit = this.RecalcInfo.AdditionalInfo.XLimit;
                        YLimit = this.RecalcInfo.AdditionalInfo.YLimit;

                        // Пересчет нужнен для обновления номеров колонок и страниц
                        Element.Reset(X, Y, XLimit, YLimit, PageIndex, 0, 1);
                        RecalcResult = Element.Recalculate_Page(0);
                        this.RecalcInfo.FlowObjectPage++;

                        if (RecalcResult & recalcresult_NextElement)
                            this.RecalcInfo.Reset();
                    }
                }
                else
                {
                    RecalcResult = Element.Recalculate_Page(PageIndex - Element.PageNum);
                    this.RecalcInfo.FlowObjectPage++;

                    if (this.DrawingObjects)
                        this.DrawingObjects.addFloatTable(new CFlowTable(Element, PageIndex));

                    if (RecalcResult & recalcresult_NextElement)
                        this.RecalcInfo.Reset();
                }
            }
            else
            {
                RecalcResult = recalcresult_NextElement;
            }
        }
        else if (type_Paragraph === Element.GetType() && true != Element.Is_Inline())
        {
            // TODO: Пока обрабатываем рамки только внутри верхнего класса внутри колонтитулов. Разобраться как и
            //       главное когда они работают внутри таблиц и автофигур.

            bFlow = true;

            if (true === this.RecalcInfo.Can_RecalcObject())
            {
                var FramePr = Element.Get_FramePr();

                // Рассчитаем количество подряд идущих параграфов с одинаковыми FramePr
                var FlowCount = 1;
                for (var TempIndex = Index + 1; TempIndex < Count; TempIndex++)
                {
                    var TempElement = this.Content[TempIndex];
                    if (type_Paragraph === TempElement.GetType() && true != TempElement.Is_Inline())
                    {
                        var TempFramePr = TempElement.Get_FramePr();
                        if (true === FramePr.Compare(TempFramePr))
                            FlowCount++;
                        else
                            break;
                    }
                    else
                        break;
                }

                var LD_PageLimits = this.LogicDocument.Get_PageLimits(PageIndex + this.Get_StartPage_Absolute());
                var LD_PageFields = this.LogicDocument.Get_PageFields(PageIndex + this.Get_StartPage_Absolute());

                var Page_W = LD_PageLimits.XLimit;
                var Page_H = LD_PageLimits.YLimit;

                var Page_Field_L = LD_PageFields.X;
                var Page_Field_R = LD_PageFields.XLimit;
                var Page_Field_T = LD_PageFields.Y;
                var Page_Field_B = LD_PageFields.YLimit;

                //--------------------------------------------------------------------------------------------------
                // 1. Рассчитаем размер рамки
                //--------------------------------------------------------------------------------------------------
                var FrameH = 0;
                var FrameW = -1;

                var Frame_XLimit = FramePr.Get_W();
                var Frame_YLimit = FramePr.Get_H();

                if (undefined === Frame_XLimit)
                    Frame_XLimit = Page_Field_R - Page_Field_L;

                if (undefined === Frame_YLimit)
                    Frame_YLimit = Page_H;

                for (var TempIndex = Index; TempIndex < Index + FlowCount; TempIndex++)
                {
                    var TempElement = this.Content[TempIndex];
                    // Получим параметры расположения рамки
                    TempElement.Set_DocumentIndex(TempIndex);

                    if (Index != TempIndex || ( true != this.RecalcInfo.FrameRecalc && ( ( 0 === Index && 0 === PageIndex ) || Index != StartIndex ) ))
                        TempElement.Reset(0, FrameH, Frame_XLimit, Frame_YLimit, PageIndex);

                    TempElement.Recalculate_Page(PageIndex);

                    FrameH = TempElement.Get_PageBounds(PageIndex - TempElement.Get_StartPage_Relative()).Bottom;
                }

                // Обработаем "авто" ширину рамки. Ширина "авто" может быть в случае, когда значение W в FramePr
                // отсутствует, когда, у нас ровно 1 параграф, с 1 строкой.
                if (-1 === FrameW && 1 === FlowCount && 1 === Element.Lines.length && undefined === FramePr.Get_W())
                {
                    FrameW     = Element.GetAutoWidthForDropCap();
                    var ParaPr = Element.Get_CompiledPr2(false).ParaPr;
                    FrameW += ParaPr.Ind.Left + ParaPr.Ind.FirstLine;

                    // Если прилегание в данном случае не к левой стороне, тогда пересчитываем параграф,
                    // с учетом того, что ширина буквицы должна быть FrameW
                    if (AscCommon.align_Left != ParaPr.Jc)
                    {
                        TempElement.Reset(0, 0, FrameW, Frame_YLimit, PageIndex);
                        TempElement.Recalculate_Page(PageIndex);
                        FrameH = TempElement.Get_PageBounds(PageIndex - TempElement.Get_StartPage_Relative()).Bottom;
                    }
                }
                else if (-1 === FrameW)
                    FrameW = Frame_XLimit;

                var FrameHRule = ( undefined === FramePr.HRule ? Asc.linerule_Auto : FramePr.HRule );
                switch (FrameHRule)
                {
                    case Asc.linerule_Auto :
                        break;
                    case Asc.linerule_AtLeast :
                    {
                        if (FrameH < FramePr.H)
                            FrameH = FramePr.H;

                        break;
                    }

                    case Asc.linerule_Exact:
                    {
                        FrameH = FramePr.H;
                        break;
                    }
                }

                //--------------------------------------------------------------------------------------------------
                // 2. Рассчитаем положение рамки
                //--------------------------------------------------------------------------------------------------

                // Теперь зная размеры рамки можем рассчитать ее позицию
                var FrameHAnchor = ( FramePr.HAnchor === undefined ? c_oAscHAnchor.Margin : FramePr.HAnchor );
                var FrameVAnchor = ( FramePr.VAnchor === undefined ? c_oAscVAnchor.Text : FramePr.VAnchor );

                // Рассчитаем положение по горизонтали
                var FrameX = 0;
                if (undefined != FramePr.XAlign || undefined === FramePr.X)
                {
                    var XAlign = c_oAscXAlign.Left;
                    if (undefined != FramePr.XAlign)
                        XAlign = FramePr.XAlign;

                    switch (FrameHAnchor)
                    {
                        case c_oAscHAnchor.Page   :
                        {
                            switch (XAlign)
                            {
                                case c_oAscXAlign.Inside  :
                                case c_oAscXAlign.Outside :
                                case c_oAscXAlign.Left    :
                                    FrameX = Page_Field_L - FrameW;
                                    break;
                                case c_oAscXAlign.Right   :
                                    FrameX = Page_Field_R;
                                    break;
                                case c_oAscXAlign.Center  :
                                    FrameX = (Page_W - FrameW) / 2;
                                    break;
                            }

                            break;
                        }
                        case c_oAscHAnchor.Text   :
                        case c_oAscHAnchor.Margin :
                        {
                            switch (XAlign)
                            {
                                case c_oAscXAlign.Inside  :
                                case c_oAscXAlign.Outside :
                                case c_oAscXAlign.Left    :
                                    FrameX = Page_Field_L;
                                    break;
                                case c_oAscXAlign.Right   :
                                    FrameX = Page_Field_R - FrameW;
                                    break;
                                case c_oAscXAlign.Center  :
                                    FrameX = (Page_Field_R + Page_Field_L - FrameW) / 2;
                                    break;
                            }

                            break;
                        }
                    }

                }
                else
                {
                    switch (FrameHAnchor)
                    {
                        case c_oAscHAnchor.Page   :
                            FrameX = FramePr.X;
                            break;
                        case c_oAscHAnchor.Text   :
                        case c_oAscHAnchor.Margin :
                            FrameX = Page_Field_L + FramePr.X;
                            break;
                    }
                }

                if (FrameW + FrameX > Page_W)
                    FrameX = Page_W - FrameW;

                if (FrameX < 0)
                    FrameX = 0;

                // Рассчитаем положение по вертикали
                var FrameY = 0;
                if (undefined != FramePr.YAlign)
                {
                    var YAlign = FramePr.YAlign;
                    // Случай c_oAscYAlign.Inline не обрабатывается, потому что такие параграфы считаются Inline

                    switch (FrameVAnchor)
                    {
                        case c_oAscVAnchor.Page   :
                        {
                            switch (YAlign)
                            {
                                case c_oAscYAlign.Inside  :
                                case c_oAscYAlign.Outside :
                                case c_oAscYAlign.Top     :
                                    FrameY = 0;
                                    break;
                                case c_oAscYAlign.Bottom  :
                                    FrameY = Page_H - FrameH;
                                    break;
                                case c_oAscYAlign.Center  :
                                    FrameY = (Page_H - FrameH) / 2;
                                    break;
                            }

                            break;
                        }
                        case c_oAscVAnchor.Text   :
                        {
                            FrameY = Y;
                            break;
                        }
                        case c_oAscVAnchor.Margin :
                        {
                            switch (YAlign)
                            {
                                case c_oAscYAlign.Inside  :
                                case c_oAscYAlign.Outside :
                                case c_oAscYAlign.Top     :
                                    FrameY = Page_Field_T;
                                    break;
                                case c_oAscYAlign.Bottom  :
                                    FrameY = Page_Field_B - FrameH;
                                    break;
                                case c_oAscYAlign.Center  :
                                    FrameY = (Page_Field_B + Page_Field_T - FrameH) / 2;
                                    break;
                            }

                            break;
                        }
                    }
                }
                else
                {
                    var FramePrY = 0;
                    if (undefined != FramePr.Y)
                        FramePrY = FramePr.Y;

                    switch (FrameVAnchor)
                    {
                        case c_oAscVAnchor.Page   :
                            FrameY = FramePrY;
                            break;
                        case c_oAscVAnchor.Text   :
                            FrameY = FramePrY + Y;
                            break;
                        case c_oAscVAnchor.Margin :
                            FrameY = FramePrY + Page_Field_T;
                            break;
                    }
                }

                if (FrameH + FrameY > Page_H)
                    FrameY = Page_H - FrameH;

                // TODO: Пересмотреть, почему эти погрешности возникают
                // Избавляемся от погрешности
                FrameY += 0.001;
                FrameH -= 0.002;

                if (FrameY < 0)
                    FrameY = 0;

                var FrameBounds = this.Content[Index].Get_FrameBounds(FrameX, FrameY, FrameW, FrameH);
                var FrameX2     = FrameBounds.X, FrameY2 = FrameBounds.Y, FrameW2 = FrameBounds.W, FrameH2 = FrameBounds.H;

                if ((FrameY2 + FrameH2 > YLimit || Y > YLimit - 0.001 ) && Index != StartIndex)
                {
                    this.RecalcInfo.Set_FrameRecalc(true);
                    this.Content[Index].StartFromNewPage();
                    RecalcResult = recalcresult_NextPage;
                }
                else
                {
                    this.RecalcInfo.Set_FrameRecalc(false);
                    for (var TempIndex = Index; TempIndex < Index + FlowCount; TempIndex++)
                    {
                        var TempElement = this.Content[TempIndex];
                        TempElement.Shift(TempElement.Pages.length - 1, FrameX, FrameY);
                        TempElement.Set_CalculatedFrame(FrameX, FrameY, FrameW, FrameH, FrameX2, FrameY2, FrameW2, FrameH2, PageIndex);
                    }

                    var FrameDx = ( undefined === FramePr.HSpace ? 0 : FramePr.HSpace );
                    var FrameDy = ( undefined === FramePr.VSpace ? 0 : FramePr.VSpace );

                    this.DrawingObjects.addFloatTable(new CFlowParagraph(Element, FrameX2, FrameY2, FrameW2, FrameH2, FrameDx, FrameDy, Index, FlowCount, FramePr.Wrap));

                    Index += FlowCount - 1;

                    if (FrameY >= Y)
                        RecalcResult = recalcresult_NextElement;
                    else
                    {
                        this.RecalcInfo.Set_FlowObject(Element, FlowCount, recalcresult_NextElement, FlowCount);
                        RecalcResult = recalcresult_CurPage;
                    }
                }
            }
            else if (true === this.RecalcInfo.Check_FlowObject(Element))
            {
                Index += this.RecalcInfo.FlowObjectPage - 1;
                this.RecalcInfo.Reset();
                RecalcResult = recalcresult_NextElement;
            }
            else
            {
                // Пропускаем
                RecalcResult = recalcresult_NextElement;
            }
        }
        else
        {
            if (( 0 === Index && 0 === PageIndex ) || Index != StartIndex)
            {
                Element.Set_DocumentIndex(Index);
                Element.Reset(X, Y, XLimit, YLimit, PageIndex, 0, 1);
            }

            if (Index === Count - 1 && Index > 0 && type_Paragraph === Element.GetType() && type_Table === this.Content[Index - 1].GetType() && true === Element.IsEmpty() && true === this.IsTableCellContent())
            {
                RecalcResult = recalcresult_NextElement;

                this.private_RecalculateEmptySectionParagraph(Element, this.Content[Index - 1], PageIndex, 0, 1);

                // Добавим в список особых параграфов
                this.Pages[PageIndex].EndSectionParas.push(Element);

                // Выставляем этот флаг, чтобы у нас не менялось значение по Y
                bFlow = true;
            }
            else
            {

                var ElementPageIndex = this.private_GetElementPageIndex(Index, PageIndex, 0, 1);
                RecalcResult         = Element.Recalculate_Page(ElementPageIndex);
            }
        }

        if (true != bFlow)
        {
            var ElementPageIndex = this.private_GetElementPageIndex(Index, PageIndex, 0, 1);
            Y                    = Element.Get_PageBounds(ElementPageIndex).Bottom;
        }

        if (RecalcResult & recalcresult_CurPage)
        {
        	if (true === this.IsBlockLevelSdtContent())
        		return recalcresult2_CurPage;

            // Такое не должно приходить в автофигурах, только в таблицах основного документа. Проверка на это находится в параграфе.
            if (RecalcResult & recalcresultflags_Footnotes)
				return recalcresult2_CurPage | recalcresultflags_Column | recalcresultflags_Footnotes;

            return this.Recalculate_Page(PageIndex, false);
        }
        else if (RecalcResult & recalcresult_NextElement)
        {
            // Ничего не делаем
        }
        else if (RecalcResult & recalcresult_NextPage)
        {
            this.Pages[PageIndex].EndPos = Index;
            Result                       = recalcresult2_NextPage;
            break;
        }
    }

    this.Pages[PageIndex].Bounds.Left   = X;
    this.Pages[PageIndex].Bounds.Top    = StartY;
    this.Pages[PageIndex].Bounds.Right  = XLimit;
    this.Pages[PageIndex].Bounds.Bottom = Y;

    if (Index >= Count)
    {
        this.Pages[PageIndex].EndPos = Count - 1;
        if (undefined != this.Parent.OnEndRecalculate_Page)
            this.Parent.OnEndRecalculate_Page(true);
    }
    else
    {
        if (undefined != this.Parent.OnEndRecalculate_Page)
            this.Parent.OnEndRecalculate_Page(false);
    }
    return Result;
};
CDocumentContent.prototype.RecalculateContent = function(fWidth, fHeight, nStartPage)
{
    this.Set_StartPage(nStartPage);
    this.Reset(0, 0, fWidth, 20000);
    var nRecalcResult = recalcresult2_NextPage;
    var nCurPage = 0;
    while ( recalcresult2_End !== nRecalcResult  )
        nRecalcResult = this.Recalculate_Page( nCurPage++, true );
};
CDocumentContent.prototype.RecalculateMinMaxContentWidth = function(isRotated)
{
	var Min   = 0;
	var Max   = 0;
	var Count = this.Content.length;

	if (true === isRotated)
	{
		for (var Pos = 0; Pos < Count; ++Pos)
		{
			var Element   = this.Content[Pos];
			var CurMinMax = Element.RecalculateMinMaxContentWidth(isRotated);

			Min += CurMinMax.Min;
			Max += CurMinMax.Max;
		}
	}
	else
	{
		for (var Pos = 0; Pos < Count; Pos++)
		{
			var Element   = this.Content[Pos];
			var CurMinMax = Element.RecalculateMinMaxContentWidth(isRotated);

			if (Min < CurMinMax.Min)
				Min = CurMinMax.Min;

			if (Max < CurMinMax.Max)
				Max = CurMinMax.Max;
		}
	}

	return {Min : Min, Max : Max};
};
CDocumentContent.prototype.SaveRecalculateObject = function()
{
	var RecalcObj = new CDocumentRecalculateObject();
	RecalcObj.Save(this);
	return RecalcObj;
};
CDocumentContent.prototype.LoadRecalculateObject = function(RecalcObj)
{
	RecalcObj.Load(this);
};
CDocumentContent.prototype.PrepareRecalculateObject = function()
{
	this.ClipInfo = [];
	this.Pages    = [];
	var Count     = this.Content.length;
	for (var Index = 0; Index < Count; Index++)
	{
		this.Content[Index].PrepareRecalculateObject();
	}
};
CDocumentContent.prototype.ReDraw = function(StartPage, EndPage)
{
	if ("undefined" === typeof(StartPage))
		StartPage = this.Get_StartPage_Absolute();
	if ("undefined" === typeof(EndPage))
		EndPage = StartPage + this.Pages.length - 1;

	this.Parent.OnContentReDraw(StartPage, EndPage);
};
CDocumentContent.prototype.OnContentRecalculate = function(bNeedRecalc, PageNum, DocumentIndex)
{
	if (false === bNeedRecalc)
	{
		this.Parent.OnContentRecalculate(false, false);
	}
	else
	{
		// Ставим номер +1, потому что текущий элемент уже рассчитан
		this.Recalculate(false, DocumentIndex + 1);
	}
};
CDocumentContent.prototype.OnContentReDraw = function(StartPage, EndPage)
{
	this.Parent.OnContentReDraw(StartPage, EndPage);
};
CDocumentContent.prototype.Draw                           = function(nPageIndex, pGraphics)
{
    var CurPage = nPageIndex - this.StartPage;
    if (CurPage < 0 || CurPage >= this.Pages.length)
        return;

    if (pGraphics.Start_Command)
    {
        pGraphics.Start_Command(AscFormat.DRAW_COMMAND_CONTENT);
    }

    var ClipInfo = this.ClipInfo[CurPage];
    if (ClipInfo)
    {
        // TODO: При клипе, как правило, обрезается сверху и снизу по 1px, поэтому введем небольшую коррекцию
        var Correction = 0;
        if (null !== this.DrawingDocument)
            Correction = this.DrawingDocument.GetMMPerDot(1);

        var Bounds = this.Pages[CurPage].Bounds;
        pGraphics.SaveGrState();
        pGraphics.AddClipRect(ClipInfo.X0, Bounds.Top - Correction, Math.abs(ClipInfo.X1 - ClipInfo.X0), Bounds.Bottom - Bounds.Top + Correction);
    }


    if (this.LogicDocument)
        this.LogicDocument.DrawingObjects.drawWrappingObjectsInContent(this.Get_AbsolutePage(CurPage), pGraphics, this);

    var Page_StartPos = this.Pages[CurPage].Pos;
    var Page_EndPos   = this.Pages[CurPage].EndPos;
    for (var Index = Page_StartPos; Index <= Page_EndPos; Index++)
    {
        var ElementPageIndex = this.private_GetElementPageIndex(Index, CurPage, 0, 1);
        this.Content[Index].Draw(ElementPageIndex, pGraphics);
    }


    if (ClipInfo)
    {
        pGraphics.RestoreGrState();
    }

    if (pGraphics.End_Command)
    {
        pGraphics.End_Command();
    }
};
CDocumentContent.prototype.GetAllComments = function(AllComments)
{
	if (undefined === AllComments)
		AllComments = [];

	var Count = this.Content.length;
	for (var Pos = 0; Pos < Count; Pos++)
	{
		var Item = this.Content[Pos];
		Item.GetAllComments(AllComments);
	}

	return AllComments;
};
CDocumentContent.prototype.GetAllMaths = function(AllMaths)
{
	if (undefined === AllMaths)
		AllMaths = [];

	var Count = this.Content.length;
	for (var Pos = 0; Pos < Count; Pos++)
	{
		var Item = this.Content[Pos];
		Item.GetAllMaths(AllMaths);
	}

	return AllMaths;
};
CDocumentContent.prototype.GetAllFloatElements = function(FloatObjs)
{
	if (undefined === FloatObjs)
		FloatObjs = [];

	var Count = this.Content.length;
	for (var Pos = 0; Pos < Count; Pos++)
	{
		var Item = this.Content[Pos];

		if (true !== Item.Is_Inline())
			FloatObjs.push(Item);

		Item.GetAllFloatElements(FloatObjs);
	}

	return FloatObjs;
};
CDocumentContent.prototype.Shift = function(CurPage, Dx, Dy)
{
	this.Pages[CurPage].Shift(Dx, Dy);

	if (this.ClipInfo[CurPage])
	{
		this.ClipInfo[CurPage].X0 += Dx;
		this.ClipInfo[CurPage].X1 += Dx;
	}

	var StartPos = this.Pages[CurPage].Pos;
	var EndPos   = this.Pages[CurPage].EndPos;
	for (var Index = StartPos; Index <= EndPos; Index++)
	{
		var Element          = this.Content[Index];
		var ElementPageIndex = this.private_GetElementPageIndex(Index, CurPage, 0, 1);
		Element.Shift(ElementPageIndex, Dx, Dy);
	}
};
CDocumentContent.prototype.UpdateEndInfo = function()
{
	for (var Index = 0, Count = this.Content.length; Index < Count; Index++)
	{
		this.Content[Index].UpdateEndInfo();
	}
};
CDocumentContent.prototype.RecalculateCurPos = function()
{
	if (docpostype_Content === this.CurPos.Type)
	{
		if (this.CurPos.ContentPos >= 0 && undefined != this.Content[this.CurPos.ContentPos])
		{
			this.private_CheckCurPage();

			if (this.CurPage > 0 && true === this.Parent.Is_HdrFtr(false))
			{
				this.CurPage = 0;
				this.DrawingDocument.TargetEnd();
			}
			else
				return this.Content[this.CurPos.ContentPos].RecalculateCurPos();
		}
	}
	else // if ( docpostype_DrawingObjects === this.CurPos.Type )
	{
		return this.LogicDocument.DrawingObjects.recalculateCurPos();
	}

	return null;
};
CDocumentContent.prototype.Get_PageBounds = function(CurPage, Height, bForceCheckDrawings)
{
	if (this.Pages.length <= 0)
		return new CDocumentBounds(0, 0, 0, 0);

	if (CurPage < 0)
		CurPage = 0;

	if (CurPage >= this.Pages.length)
		CurPage = this.Pages.length - 1;

	var Bounds  = this.Pages[CurPage].Bounds;
	var PageAbs = this.Get_AbsolutePage(CurPage);

	// В колонтитуле не учитывается.
	if ((true != this.Is_HdrFtr(false) && true !== this.IsBlockLevelSdtContent()) || true === bForceCheckDrawings)
	{
		// Учитываем все Drawing-объекты с обтеканием. Объекты без обтекания (над и под текстом) учитываем только в
		// случае, когда начальная точка (левый верхний угол) попадает в this.Y + Height

		var AllDrawingObjects = this.GetAllDrawingObjects();
		var Count             = AllDrawingObjects.length;
		for (var Index = 0; Index < Count; Index++)
		{
			var Obj = AllDrawingObjects[Index];
			if (PageAbs === Obj.Get_PageNum())
			{
				var ObjBounds = Obj.Get_Bounds();
				if (true === Obj.Use_TextWrap())
				{
					if (ObjBounds.Bottom > Bounds.Bottom)
						Bounds.Bottom = ObjBounds.Bottom;
				}
				else if (undefined !== Height && ObjBounds.Top < this.Y + Height)
				{
					if (ObjBounds.Bottom >= this.Y + Height)
						Bounds.Bottom = this.Y + Height;
					else if (ObjBounds.Bottom > Bounds.Bottom)
						Bounds.Bottom = ObjBounds.Bottom;
				}
			}
		}

		// Кроме этого пробежимся по всем Flow-таблицам и учтем их границы
		var Count = this.Content.length;
		for (var Index = 0; Index < Count; Index++)
		{
			var Element          = this.Content[Index];
			var ElementPageIndex = this.private_GetElementPageIndex(Index, CurPage, 0, 1);
			if (type_Table === Element.GetType() && true != Element.Is_Inline() && 0 <= ElementPageIndex && ElementPageIndex < Element.Get_PagesCount())
			{
				var TableBounds = Element.Get_PageBounds(ElementPageIndex);
				if (TableBounds.Bottom > Bounds.Bottom)
					Bounds.Bottom = TableBounds.Bottom;
			}
		}
	}

	return Bounds;
};
CDocumentContent.prototype.GetContentBounds = function(CurPage)
{
	var oPage = this.Pages[CurPage];
	if (!oPage || oPage.Pos > oPage.EndPos)
		return this.Get_PageBounds(CurPage);

	var oBounds = null;
	for (var nIndex = oPage.Pos; nIndex <= oPage.EndPos; ++nIndex)
	{
		var oElement          = this.Content[nIndex];
		var nElementPageIndex = this.private_GetElementPageIndex(nIndex, CurPage, 0, 1);

		var oElementBounds = oElement.GetContentBounds(nElementPageIndex);

		if (null === oBounds)
		{
			oBounds = oElementBounds.Copy();
		}
		else
		{
			if (oElementBounds.Bottom > oBounds.Bottom)
				oBounds.Bottom = oElementBounds.Bottom;

			if (oElementBounds.Top < oBounds.Top)
				oBounds.Top = oElementBounds.Top;

			if (oElementBounds.Right > oBounds.Right)
				oBounds.Right = oElementBounds.Right;

			if (oElementBounds.Left < oBounds.Left)
				oBounds.Left = oElementBounds.Left;
		}
	}

	return oBounds;
};
CDocumentContent.prototype.Get_PagesCount = function()
{
	return this.Pages.length;
};
CDocumentContent.prototype.Get_SummaryHeight = function()
{
	var Height = 0;
	for (var Page = 0; Page < this.Get_PagesCount(); Page++)
	{
		var Bounds = this.Get_PageBounds(Page);
		Height += Bounds.Bottom - Bounds.Top;
	}

	return Height;
};
CDocumentContent.prototype.Get_FirstParagraph = function()
{
	if (this.Content.length > 0)
		return this.Content[0].Get_FirstParagraph();

	return null;
};
CDocumentContent.prototype.GetAllParagraphs = function(Props, ParaArray)
{
	var arrParagraphs = (ParaArray ? ParaArray : []);

	var Count = this.Content.length;
	for (var Index = 0; Index < Count; Index++)
	{
		var Element = this.Content[Index];
		Element.GetAllParagraphs(Props, arrParagraphs);
	}

	return arrParagraphs;
};
// Специальная функция, используемая в колонтитулах для добавления номера страницы
// При этом удаляются все параграфы. Добавляются два новых
CDocumentContent.prototype.HdrFtr_AddPageNum             = function(Align, StyleId)
{
    this.RemoveSelection();

    this.CurPos =
    {
        X          : 0,
        Y          : 0,
        ContentPos : 0,
        RealX      : 0,
        RealY      : 0,
        Type       : docpostype_Content
    };

    this.Selection.Use = false;

    // Удаляем все элементы
    this.Internal_Content_RemoveAll();

    // Добавляем 2 новых параграфа
    var Para1 = new Paragraph(this.DrawingDocument, this, this.bPresentation === true);
    var Para2 = new Paragraph(this.DrawingDocument, this, this.bPresentation === true);

    this.Internal_Content_Add(0, Para1);
    this.Internal_Content_Add(1, Para2);

    Para1.Set_DocumentPrev(null);
    Para1.Set_DocumentNext(Para2);
    Para2.Set_DocumentPrev(Para1);
    Para2.Set_DocumentNext(null);

    Para1.Style_Add(StyleId);
    Para2.Style_Add(StyleId);

    Para1.Set_Align(Align, false);
    var Run = new ParaRun(Para1, false);
    Run.Add_ToContent(0, new ParaPageNum());
    Para1.Add_ToContent(0, Run);

    this.Recalculate();
};
CDocumentContent.prototype.Clear_Content                 = function()
{
    this.RemoveSelection();

    this.CurPos =
    {
        X          : 0,
        Y          : 0,
        ContentPos : 0,
        RealX      : 0,
        RealY      : 0,
        Type       : docpostype_Content
    };

    this.Selection.Use = false;

    // Удаляем все элементы
    this.Internal_Content_RemoveAll();

    // Добавляем новый параграф
    var Para = new Paragraph(this.DrawingDocument, this, this.bPresentation === true);
    this.Internal_Content_Add(0, Para);
};
CDocumentContent.prototype.Add_Content                   = function(OtherContent)
{
    if ("object" != typeof(OtherContent) || 0 >= OtherContent.Content.length || true === OtherContent.Is_Empty())
        return;

    // TODO : улучшить добавление элементов здесь (чтобы добавлялось не поэлементно)
    if (true === this.Is_Empty())
    {
        this.Internal_Content_RemoveAll();
        for (var Index = 0; Index < OtherContent.Content.length; Index++)
            this.Internal_Content_Add(Index, OtherContent.Content[Index]);
    }
    else
    {
        this.Content[this.Content.length - 1].Set_DocumentNext(OtherContent.Content[0]);
        OtherContent.Content[0].Set_DocumentPrev(this.Content[this.Content.length - 1]);

        for (var Index = 0; Index < OtherContent.Content.length; Index++)
        {
            this.Internal_Content_Add(this.Content.length, OtherContent.Content[Index]);
        }
    }
};
CDocumentContent.prototype.Is_Empty = function()
{
	if (this.Content.length > 1 || type_Paragraph !== this.Content[0].GetType())
		return false;

	return this.Content[0].IsEmpty();
};
CDocumentContent.prototype.Is_CurrentElementTable = function()
{
	if (docpostype_DrawingObjects == this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.isCurrentElementTable();
	}
	else if (docpostype_Content == this.CurPos.Type && ( ( true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Table == this.Content[this.Selection.StartPos].GetType() ) || ( false == this.Selection.Use && type_Table == this.Content[this.CurPos.ContentPos].GetType() ) ))
	{
		return true;
	}
	return false;
};
CDocumentContent.prototype.Is_CurrentElementParagraph = function()
{
	if (docpostype_DrawingObjects == this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.isCurrentElementParagraph();
	}
	else if (docpostype_Content == this.CurPos.Type && ( ( true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Table == this.Content[this.Selection.StartPos].GetType() ) || ( false == this.Selection.Use && type_Table == this.Content[this.CurPos.ContentPos].GetType() ) ))
	{
		return false;
	}

	return true;
};
CDocumentContent.prototype.GetCurrentParagraph = function(bIgnoreSelection, arrSelectedParagraphs)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.getCurrentParagraph(bIgnoreSelection, arrSelectedParagraphs);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (arrSelectedParagraphs)
		{
			var nStartPos = this.Selection.StartPos <= this.Selection.EndPos ? this.Selection.StartPos : this.Selection.EndPos;
			var nEndPos   = this.Selection.StartPos <= this.Selection.EndPos ? this.Selection.EndPos : this.Selection.StartPos;
			for (var nPos = nStartPos; nPos <= nEndPos; ++nPos)
			{
				this.Content[nPos].GetCurrentParagraph(false, arrSelectedParagraphs);
			}
		}
		else
		{
			var Pos = true === this.Selection.Use && true !== bIgnoreSelection ? this.Selection.StartPos : this.CurPos.ContentPos;
			if (Pos < 0 || Pos >= this.Content.length)
				return null;

			return this.Content[Pos].GetCurrentParagraph(bIgnoreSelection, null);
		}
	}

	return null;
};
CDocumentContent.prototype.IsContentOnFirstPage = function()
{
	if (this.Content.length <= 0)
		return false;

	var Element = this.Content[0];
	return Element.IsContentOnFirstPage();
};
CDocumentContent.prototype.StartFromNewPage = function()
{
	this.Pages.length = 1;
	this.Pages[0]     = new CDocumentPage();

	var Element = this.Content[0];
	Element.StartFromNewPage();
};
CDocumentContent.prototype.Get_ParentTextTransform = function()
{
	if (this.Parent)
		return this.Parent.Get_ParentTextTransform();

	return null;
};
CDocumentContent.prototype.IsTableBorder = function(X, Y, CurPage)
{
	CurPage = Math.max(0, Math.min(this.Pages.length - 1, CurPage));

	var ElementPos       = this.Internal_GetContentPosByXY(X, Y, CurPage);
	var Element          = this.Content[ElementPos];
	var ElementPageIndex = this.private_GetElementPageIndex(ElementPos, CurPage, 0, 1);
	return Element.IsTableBorder(X, Y, ElementPageIndex);
};
CDocumentContent.prototype.IsInText = function(X, Y, CurPage)
{
	if (CurPage < 0 || CurPage >= this.Pages.length)
		CurPage = 0;

	var ContentPos       = this.Internal_GetContentPosByXY(X, Y, CurPage);
	var Item             = this.Content[ContentPos];
	var ElementPageIndex = this.private_GetElementPageIndexByXY(ContentPos, X, Y, CurPage);
	return Item.IsInText(X, Y, ElementPageIndex);
};
CDocumentContent.prototype.IsInDrawing = function(X, Y, CurPage)
{
	if (-1 != this.DrawingObjects.IsInDrawingObject(X, Y, this.Get_AbsolutePage(CurPage), this))
	{
		return true;
	}
	else
	{
		if (CurPage < 0 || CurPage >= this.Pages.length)
			CurPage = 0;

		var ContentPos = this.Internal_GetContentPosByXY(X, Y, CurPage);
		var Item       = this.Content[ContentPos];
		if (type_Table == Item.GetType())
		{
			var ElementPageIndex = this.private_GetElementPageIndexByXY(ContentPos, X, Y, CurPage);
			return Item.IsInDrawing(X, Y, ElementPageIndex);
		}

		return false;
	}
};
CDocumentContent.prototype.Get_CurrentPage_Absolute = function()
{
	if (docpostype_DrawingObjects == this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.getCurrentPageAbsolute();
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		var Pos = ( true === this.Selection.Use && selectionflag_Numbering !== this.Selection.Flag ? this.Selection.EndPos : this.CurPos.ContentPos );
		if (Pos >= 0 && Pos < this.Content.length)
			return this.Content[Pos].Get_CurrentPage_Absolute();
	}

	return 0;
};
CDocumentContent.prototype.Get_CurrentPage_Relative = function()
{
	return this.CurPage;
};
CDocumentContent.prototype.CollectDocumentStatistics = function(Stats)
{
	var Count = this.Content.length;
	for (var Index = 0; Index < Count; Index++)
	{
		var Element = this.Content[Index];
		Element.CollectDocumentStatistics(Stats);
	}
};
CDocumentContent.prototype.Document_CreateFontMap = function(FontMap)
{
	var Count = this.Content.length;
	for (var Index = 0; Index < Count; Index++)
	{
		var Element = this.Content[Index];
		Element.Document_CreateFontMap(FontMap);
	}
};
CDocumentContent.prototype.Document_CreateFontCharMap = function(FontCharMap)
{
	var Count = this.Content.length;
	for (var Index = 0; Index < Count; Index++)
	{
		var Element = this.Content[Index];
		Element.Document_CreateFontCharMap(FontCharMap);
	}
};
CDocumentContent.prototype.Document_Get_AllFontNames = function(AllFonts)
{
	var Count = this.Content.length;
	for (var Index = 0; Index < Count; Index++)
	{
		var Element = this.Content[Index];
		Element.Document_Get_AllFontNames(AllFonts);
	}
};
CDocumentContent.prototype.Document_UpdateInterfaceState = function()
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		var drawin_objects = this.LogicDocument.DrawingObjects;
		if (drawin_objects.selection.textSelection
			|| drawin_objects.selection.groupSelection && drawin_objects.selection.groupSelection.selection.textSelection
			|| drawin_objects.selection.chartSelection && drawin_objects.selection.chartSelection.selection.textSelection)
		{
			this.LogicDocument.Interface_Update_DrawingPr();
			drawin_objects.documentUpdateInterfaceState();
		}
		else
		{
			drawin_objects.documentUpdateInterfaceState();
			this.LogicDocument.Interface_Update_DrawingPr();
		}
		return;
	}
	else //if (docpostype_Content === this.CurPos.Type)
	{
		if ((true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType())
			|| (false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType()))
		{
			this.Interface_Update_TablePr();
			if (true == this.Selection.Use)
				this.Content[this.Selection.StartPos].Document_UpdateInterfaceState();
			else
				this.Content[this.CurPos.ContentPos].Document_UpdateInterfaceState();
		}
		else
		{
			this.Interface_Update_ParaPr();
			this.Interface_Update_TextPr();

			// Если у нас в выделении находится 1 параграф, или курсор находится в параграфе
			if ((true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph == this.Content[this.Selection.StartPos].GetType())
				|| (false == this.Selection.Use && type_Paragraph == this.Content[this.CurPos.ContentPos].GetType()))
			{
				if (true == this.Selection.Use)
					this.Content[this.Selection.StartPos].Document_UpdateInterfaceState();
				else
					this.Content[this.CurPos.ContentPos].Document_UpdateInterfaceState();
			}
		}
	}
};
CDocumentContent.prototype.Document_UpdateRulersState = function(CurPage)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		this.LogicDocument.DrawingObjects.documentUpdateRulersState(CurPage);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (true === this.Selection.Use)
		{
			if (this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType())
			{
				var ElementPos       = this.Selection.StartPos;
				var Element          = this.Content[ElementPos];
				var ElementPageIndex = this.private_GetElementPageIndex(ElementPos, this.CurPage, Element.Get_StartColumn(), Element.Get_ColumnsCount());
				Element.Document_UpdateRulersState(ElementPageIndex);
			}
			else
			{
				var StartPos = ( this.Selection.EndPos <= this.Selection.StartPos ? this.Selection.EndPos : this.Selection.StartPos );
				var EndPos   = ( this.Selection.EndPos <= this.Selection.StartPos ? this.Selection.StartPos : this.Selection.EndPos );

				var FramePr = undefined;

				for (var Pos = StartPos; Pos <= EndPos; Pos++)
				{
					var Element = this.Content[Pos];
					if (type_Paragraph != Element.GetType())
					{
						FramePr = undefined;
						break;
					}
					else
					{
						var TempFramePr = Element.Get_FramePr();
						if (undefined === FramePr)
						{
							if (undefined === TempFramePr)
								break;

							FramePr = TempFramePr;
						}
						else if (undefined === TempFramePr || false === FramePr.Compare(TempFramePr))
						{
							FramePr = undefined;
							break;
						}
					}
				}

				if (undefined !== FramePr)
					this.Content[StartPos].Document_UpdateRulersState();
			}
		}
		else
		{
			var ElementPos       = this.CurPos.ContentPos;
			var Element          = this.Content[ElementPos];
			var ElementPageIndex = this.private_GetElementPageIndex(ElementPos, this.CurPage, Element.Get_StartColumn(), Element.Get_ColumnsCount());
			Element.Document_UpdateRulersState(ElementPageIndex);
		}
	}
};
CDocumentContent.prototype.Can_CopyCut = function()
{
	var bCanCopyCut = false;

	var LogicDocument  = null;
	var DrawingObjects = null;

	// Работаем с колонтитулом
	if (docpostype_DrawingObjects === this.CurPos.Type)
		DrawingObjects = this.DrawingObjects;
	else
		LogicDocument = this;

	if (null !== DrawingObjects)
	{
		if (true === DrawingObjects.isSelectedText())
			LogicDocument = DrawingObjects.getTargetDocContent();
		else
			bCanCopyCut = true;
	}

	if (null !== LogicDocument)
	{
		if (true === LogicDocument.IsSelectionUse())
		{
			if (selectionflag_Numbering === LogicDocument.Selection.Flag)
				bCanCopyCut = false;
			else if (LogicDocument.Selection.StartPos !== LogicDocument.Selection.EndPos)
				bCanCopyCut = true;
			else
				bCanCopyCut = LogicDocument.Content[LogicDocument.Selection.StartPos].Can_CopyCut();
		}
	}

	return bCanCopyCut;
};
CDocumentContent.prototype.MoveCursorToStartPos = function(AddToSelect)
{
	if (true === AddToSelect)
	{
		if (docpostype_DrawingObjects === this.CurPos.Type)
		{
			// TODO: Пока ничего не делаем, в дальнейшем надо будет делать в зависимости от селекта внутри
			//       автофигуры: если селект текста внутри, то делать для текста внутри, а если выделена
			//       сама автофигура, тогда мы перемещаем курсор влево от нее в контенте параграфа и выделяем все до конца
		}
		else if (docpostype_Content === this.CurPos.Type)
		{
			var StartPos = ( true === this.Selection.Use ? this.Selection.StartPos : this.CurPos.ContentPos );
			var EndPos   = 0;

			this.Selection.Start    = false;
			this.Selection.Use      = true;
			this.Selection.StartPos = StartPos;
			this.Selection.EndPos   = EndPos;
			this.Selection.Flag     = selectionflag_Common;

			this.CurPos.ContentPos = 0;
			this.Set_DocPosType(docpostype_Content);

			for (var Index = StartPos - 1; Index >= EndPos; Index--)
			{
				this.Content[Index].SelectAll(-1);
			}

			this.Content[StartPos].MoveCursorToStartPos(true);
		}
	}
	else
	{
		this.RemoveSelection();

		this.Selection.Start    = false;
		this.Selection.Use      = false;
		this.Selection.StartPos = 0;
		this.Selection.EndPos   = 0;
		this.Selection.Flag     = selectionflag_Common;

		this.CurPos.ContentPos = 0;
		this.Set_DocPosType(docpostype_Content);
		this.Content[0].MoveCursorToStartPos(false);
	}
};
CDocumentContent.prototype.MoveCursorToEndPos = function(AddToSelect, StartSelectFromEnd)
{
	if (true === AddToSelect)
	{
		if (docpostype_DrawingObjects === this.CurPos.Type)
		{
			// TODO: Пока ничего не делаем, в дальнейшем надо будет делать в зависимости от селекта внутри
			//       автофигуры: если селект текста внутри, то делать для текста внутри, а если выделена
			//       сама автофигура, тогда мы перемещаем курсор влево от нее в контенте параграфа и выделяем все до конца
		}
		else if (docpostype_Content === this.CurPos.Type)
		{
			var StartPos = ( true === this.Selection.Use ? this.Selection.StartPos : this.CurPos.ContentPos )
			var EndPos   = this.Content.length - 1;

			this.Selection.Start    = false;
			this.Selection.Use      = true;
			this.Selection.StartPos = StartPos;
			this.Selection.EndPos   = EndPos;
			this.Selection.Flag     = selectionflag_Common;

			this.CurPos.ContentPos = this.Content.length - 1;
			this.Set_DocPosType(docpostype_Content);

			for (var Index = StartPos + 1; Index <= EndPos; Index++)
			{
				this.Content[Index].SelectAll(1);
			}

			this.Content[StartPos].MoveCursorToEndPos(true);
		}
	}
	else
	{
		if (true === StartSelectFromEnd)
		{
			this.Selection.Start    = false;
			this.Selection.Use      = true;
			this.Selection.StartPos = this.Content.length - 1;
			this.Selection.EndPos   = this.Content.length - 1;
			this.Selection.Flag     = selectionflag_Common;
			this.CurPos.ContentPos  = this.Content.length - 1;
			this.Set_DocPosType(docpostype_Content);
			this.Content[this.Content.length - 1].MoveCursorToEndPos(false, true);
		}
		else
		{
			this.RemoveSelection();

			this.Selection.Start    = false;
			this.Selection.Use      = false;
			this.Selection.StartPos = 0;
			this.Selection.EndPos   = 0;
			this.Selection.Flag     = selectionflag_Common;

			this.CurPos.ContentPos = this.Content.length - 1;
			this.Set_DocPosType(docpostype_Content);
			this.Content[this.CurPos.ContentPos].MoveCursorToEndPos(false);
		}
	}
};
CDocumentContent.prototype.MoveCursorUpToLastRow = function(X, Y, AddToSelect)
{
	this.SetCurPosXY(X, Y);
	if (true === AddToSelect)
	{
		if (true !== this.Selection.Use)
		{
			this.CurPos.ContentPos = this.Content.length - 1;
			this.Set_DocPosType(docpostype_Content);
			this.Selection.Use      = true;
			this.Selection.Start    = false;
			this.Selection.StartPos = this.CurPos.ContentPos;
			this.Selection.EndPos   = this.CurPos.ContentPos;
			this.Selection.Flag     = selectionflag_Common;

			this.Content[this.CurPos.ContentPos].MoveCursorToEndPos(false, true);
			this.Content[this.CurPos.ContentPos].MoveCursorUpToLastRow(X, Y, true);
		}
		else
		{
			var StartPos = this.Selection.StartPos;
			var EndPos   = this.Content.length - 1;

			this.CurPos.ContentPos = EndPos;

			// Очистим старый селект кроме начального элемента
			var _S = this.Selection.StartPos <= this.Selection.EndPos ? this.Selection.StartPos : this.Selection.EndPos;
			var _E = this.Selection.StartPos <= this.Selection.EndPos ? this.Selection.EndPos : this.Selection.StartPos;
			for (var nPos = _S; nPos <= _E; ++nPos)
			{
				if (nPos !== StartPos)
					this.Content[nPos].RemoveSelection();
			}

			if (StartPos === EndPos)
			{
				this.Selection.StartPos = StartPos;
				this.Selection.EndPos   = StartPos;
				this.Content[StartPos].MoveCursorUpToLastRow(X, Y, true);
			}
			else
			{
				this.Content[StartPos].MoveCursorToEndPos(true);
				for (var nPos = StartPos + 1; nPos <= EndPos; ++nPos)
				{
					this.Content[nPos].SelectAll(1);
				}

				this.Content[EndPos].MoveCursorUpToLastRow(X, Y, true);
			}
		}
	}
	else
	{
		this.CurPos.ContentPos = this.Content.length - 1;
		this.Content[this.CurPos.ContentPos].MoveCursorUpToLastRow(X, Y, false);
	}
};
CDocumentContent.prototype.MoveCursorDownToFirstRow = function(X, Y, AddToSelect)
{
	this.SetCurPosXY(X, Y);
	if (true === AddToSelect)
	{
		if (true !== this.Selection.Use)
		{
			this.CurPos.ContentPos = 0;
			this.Set_DocPosType(docpostype_Content);
			this.Selection.Use      = true;
			this.Selection.Start    = false;
			this.Selection.StartPos = 0;
			this.Selection.EndPos   = 0;
			this.Selection.Flag     = selectionflag_Common;

			this.Content[0].MoveCursorToStartPos(false);
			this.Content[0].MoveCursorDownToFirstRow(X, Y, true);
		}
		else
		{
			var StartPos = this.Selection.StartPos;
			var EndPos   = 0;

			this.CurPos.ContentPos = EndPos;

			// Очистим старый селект кроме начального элемента
			var _S = this.Selection.StartPos <= this.Selection.EndPos ? this.Selection.StartPos : this.Selection.EndPos;
			var _E = this.Selection.StartPos <= this.Selection.EndPos ? this.Selection.EndPos : this.Selection.StartPos;
			for (var nPos = _S; nPos <= _E; ++nPos)
			{
				if (nPos !== StartPos)
					this.Content[nPos].RemoveSelection();
			}

			if (StartPos === EndPos)
			{
				this.Selection.StartPos = StartPos;
				this.Selection.EndPos   = StartPos;
				this.Content[StartPos].MoveCursorDownToFirstRow(X, Y, true);
			}
			else
			{
				this.Content[StartPos].MoveCursorToStartPos(true);
				for (var nPos = EndPos; nPos < StartPos; ++nPos)
				{
					this.Content[nPos].SelectAll(-1);
				}

				this.Content[EndPos].MoveCursorDownToFirstRow(X, Y, true);
			}
		}
	}
	else
	{
		this.CurPos.ContentPos = 0;
		this.Content[this.CurPos.ContentPos].MoveCursorDownToFirstRow(X, Y, false);
	}
};
CDocumentContent.prototype.MoveCursorToCell = function(bNext)
{
	if (true === this.ApplyToAll)
	{
		if (1 === this.Content.length)
			this.Content[0].MoveCursorToCell(bNext);
	}
	else
	{
		if (docpostype_DrawingObjects == this.CurPos.Type)
		{
			this.LogicDocument.DrawingObjects.cursorMoveToCell(bNext);
		}
		else //if ( docpostype_Content == this.CurPos.Type )
		{
			if (true === this.Selection.Use)
			{
				if (this.Selection.StartPos === this.Selection.EndPos)
					this.Content[this.Selection.StartPos].MoveCursorToCell(bNext);
			}
			else
			{
				this.Content[this.CurPos.ContentPos].MoveCursorToCell(bNext);
			}
		}
	}
};
CDocumentContent.prototype.Set_ClipInfo = function(CurPage, X0, X1)
{
	this.ClipInfo[CurPage] = {X0 : X0, X1 : X1};
};
CDocumentContent.prototype.Set_ApplyToAll = function(bValue)
{
	this.ApplyToAll = bValue;
};
CDocumentContent.prototype.Get_ApplyToAll = function()
{
	return this.ApplyToAll;
};
CDocumentContent.prototype.UpdateCursorType = function(X, Y, CurPage)
{
	if (CurPage < 0 || CurPage >= this.Pages.length)
		return this.DrawingDocument.SetCursorType("default", new AscCommon.CMouseMoveData());

	var bInText      = (null === this.IsInText(X, Y, CurPage) ? false : true);
	var bTableBorder = (null === this.IsTableBorder(X, Y, CurPage) ? false : true);

	// Ничего не делаем
	if (this.Parent instanceof CHeaderFooter && true === this.LogicDocument.DrawingObjects.updateCursorType(this.Get_AbsolutePage(CurPage), X, Y, {}, ( true === bInText || true === bTableBorder ? true : false )))
		return;

	var ContentPos       = this.Internal_GetContentPosByXY(X, Y, CurPage);
	var Item             = this.Content[ContentPos];
	var ElementPageIndex = this.private_GetElementPageIndexByXY(ContentPos, X, Y, CurPage);
	Item.UpdateCursorType(X, Y, ElementPageIndex);
};
//-----------------------------------------------------------------------------------
// Функции для работы с контентом
//-----------------------------------------------------------------------------------
CDocumentContent.prototype.AddNewParagraph = function()
{
    if (docpostype_DrawingObjects === this.CurPos.Type)
    {
        return this.DrawingObjects.addNewParagraph();
    }
    else //if ( docpostype_Content == this.CurPos.Type )
    {
        if (this.CurPos.ContentPos < 0)
            return false;

        // Сначала удаляем заселекченую часть
        if (true === this.Selection.Use)
        {
            this.Remove(1, true, false, true);
        }

        // Добавляем новый параграф
        var Item = this.Content[this.CurPos.ContentPos];

        // Если мы внутри параграфа, тогда:
        // 1. Если мы в середине параграфа, разделяем данный параграф на 2.
        //    При этом полностью копируем все настройки из исходного параграфа.
        // 2. Если мы в конце данного параграфа, тогда добавляем новый пустой параграф.
        //    Стиль у него проставляем такой какой указан у текущего в Style.Next.
        //    Если при этом у нового параграфа стиль будет такой же как и у старого,
        //    в том числе если стиля нет у обоих, тогда копируем еще все прямые настройки.
        //    (Т.е. если стили разные, а у исходный параграф был параграфом со списком, тогда
        //    новый параграф будет без списка).
        if (type_Paragraph === Item.GetType())
        {
            // Если текущий параграф пустой и с нумерацией, тогда удаляем нумерацию и отступы левый и первой строки
            if (undefined != Item.Numbering_Get() && true === Item.IsEmpty({SkipNewLine : true}) && true === Item.IsCursorAtBegin())
            {
                Item.Numbering_Remove();
                Item.Set_Ind({FirstLine : undefined, Left : undefined, Right : Item.Pr.Ind.Right}, true);
            }
            else
            {
                var ItemReviewType = Item.Get_ReviewType();
                // Создаем новый параграф
                var NewParagraph   = new Paragraph(this.DrawingDocument, this, this.bPresentation === true);

                // Проверим позицию в текущем параграфе
                if (true === Item.IsCursorAtEnd())
                {
                    var StyleId = Item.Style_Get();
                    var NextId  = undefined;

                    if (undefined != StyleId)
                    {
                        var Styles = this.Parent.Get_Styles();
                        NextId     = Styles.Get_Next(StyleId);

                        if (null === NextId)
                            NextId = StyleId;
                    }


                    if (StyleId === NextId)
                    {
                        // Продолжаем (в плане настроек) новый параграф
                        Item.Continue(NewParagraph);
                    }
                    else
                    {
                        // Простое добавление стиля, без дополнительных действий
                        if (NextId === this.Get_Styles().Get_Default_Paragraph())
                            NewParagraph.Style_Remove();
                        else
                            NewParagraph.Style_Add(NextId, true);
                    }

					var LastRun = Item.Content[Item.Content.length - 1];
					if (LastRun && LastRun.Pr.Lang && LastRun.Pr.Lang.Val)
					{
						NewParagraph.SelectAll();
						NewParagraph.Add(new ParaTextPr({Lang : LastRun.Pr.Lang.Copy()}));
						NewParagraph.RemoveSelection();
					}
                }
                else
                    Item.Split(NewParagraph);

                this.Internal_Content_Add(this.CurPos.ContentPos + 1, NewParagraph);
                this.CurPos.ContentPos++;

                if (true === this.Is_TrackRevisions())
                {
                    NewParagraph.Remove_PrChange();
                    NewParagraph.Set_ReviewType(ItemReviewType);
                    Item.Set_ReviewType(reviewtype_Add);
                }
                else if (reviewtype_Common !== ItemReviewType)
                {
                    NewParagraph.Set_ReviewType(ItemReviewType);
                    Item.Set_ReviewType(reviewtype_Common);
                }
            }
        }
        else if (type_Table === Item.GetType() || type_BlockLevelSdt === Item.GetType())
        {
            // Если мы находимся в начале первого параграфа первой ячейки, и
            // данная таблица - первый элемент, тогда добавляем параграф до таблицы.

            if (0 === this.CurPos.ContentPos && Item.IsCursorAtBegin(true))
            {
                // Создаем новый параграф
                var NewParagraph = new Paragraph(this.DrawingDocument, this, this.bPresentation === true);
                this.Internal_Content_Add(0, NewParagraph);
                this.CurPos.ContentPos = 0;

				if (true === this.Is_TrackRevisions())
				{
					NewParagraph.Remove_PrChange();
					NewParagraph.Set_ReviewType(reviewtype_Add);
				}
            }
            else
			{
				Item.AddNewParagraph();
			}
        }
    }
};
// Расширяем документ до точки (X,Y) с помощью новых параграфов
// Y0 - низ последнего параграфа, YLimit - предел страницы
CDocumentContent.prototype.Extend_ToPos                       = function(X, Y)
{
    var LastPara  = this.Content[this.Content.length - 1];
    var LastPara2 = LastPara;

    History.Create_NewPoint(AscDFH.historydescription_Document_DocumentContentExtendToPos);
    History.Set_Additional_ExtendDocumentToPos();

    while (true)
    {
        var NewParagraph = new Paragraph(this.DrawingDocument, this, this.bPresentation === true);
		var NewRun       = new ParaRun(NewParagraph, false);
		NewParagraph.Add_ToContent(0, NewRun);

        var StyleId = LastPara.Style_Get();
        var NextId  = undefined;

        if (undefined != StyleId)
        {
            NextId = this.Styles.Get_Next(StyleId);

            if (null === NextId || undefined === NextId)
                NextId = StyleId;
        }

        // Простое добавление стиля, без дополнительных действий
        if (NextId === this.Styles.Get_Default_Paragraph())
            NewParagraph.Style_Remove();
        else
            NewParagraph.Style_Add(NextId, true);

        if (undefined != LastPara.TextPr.Value.FontSize || undefined !== LastPara.TextPr.Value.RFonts.Ascii)
        {
            var TextPr        = new CTextPr();
            TextPr.FontSize   = LastPara.TextPr.Value.FontSize;
            TextPr.FontSizeCS = LastPara.TextPr.Value.FontSize;
            TextPr.RFonts     = LastPara.TextPr.Value.RFonts.Copy();
            NewParagraph.SelectAll();
            NewParagraph.Apply_TextPr(TextPr);
        }

        LastPara.Set_DocumentNext(NewParagraph);

        NewParagraph.Set_DocumentPrev(LastPara);
        NewParagraph.Set_DocumentIndex(LastPara.Index + 1);

        var CurPage = LastPara.Pages.length - 1;
        var X0      = LastPara.Pages[CurPage].X;
        var Y0      = LastPara.Pages[CurPage].Bounds.Bottom;
        var XLimit  = LastPara.Pages[CurPage].XLimit;
        var YLimit  = LastPara.Pages[CurPage].YLimit;
        var PageNum = LastPara.PageNum;

        NewParagraph.Reset(X0, Y0, XLimit, YLimit, PageNum);
        var RecalcResult = NewParagraph.Recalculate_Page(PageNum);

        if (!(RecalcResult & recalcresult_NextElement))
        {
            LastPara.Next = null;
            break;
        }

        this.Internal_Content_Add(this.Content.length, NewParagraph);

        if (NewParagraph.Pages[0].Bounds.Bottom > Y)
            break;

        LastPara = NewParagraph;
    }

    LastPara = this.Content[this.Content.length - 1];

    if (LastPara != LastPara2 || false === this.LogicDocument.Document_Is_SelectionLocked(AscCommon.changestype_None, {
            Type      : AscCommon.changestype_2_Element_and_Type,
            Element   : LastPara,
            CheckType : AscCommon.changestype_Paragraph_Content
        }))
    {
        // Теперь нам нужно вставить таб по X
        LastPara.Extend_ToPos(X);
    }

    LastPara.MoveCursorToEndPos();
    LastPara.Document_SetThisElementCurrent(true);

    this.LogicDocument.Recalculate();
};
CDocumentContent.prototype.AddInlineImage = function(W, H, Img, Chart, bFlow)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.DrawingObjects.addInlineImage(W, H, Img, Chart, bFlow);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (true == this.Selection.Use)
			this.Remove(1, true);

		var Item = this.Content[this.CurPos.ContentPos];
		if (type_Paragraph == Item.GetType())
		{
			var Drawing;
			if (!AscCommon.isRealObject(Chart))
			{
				Drawing   = new ParaDrawing(W, H, null, this.DrawingDocument, this, null);
				var Image = this.DrawingObjects.createImage(Img, 0, 0, W, H);
				Image.setParent(Drawing);
				Drawing.Set_GraphicObject(Image);
			}
			else
			{
				Drawing   = new ParaDrawing(W, H, null, this.DrawingDocument, this, null);
				var Image = this.DrawingObjects.getChartSpace2(Chart, null);
				Image.setParent(Drawing);
				Drawing.Set_GraphicObject(Image);
				Drawing.setExtent(Image.spPr.xfrm.extX, Image.spPr.xfrm.extY);
			}
			if (true === bFlow)
			{
				Drawing.Set_DrawingType(drawing_Anchor);
				Drawing.Set_WrappingType(WRAPPING_TYPE_SQUARE);
				Drawing.Set_BehindDoc(false);
				Drawing.Set_Distance(3.2, 0, 3.2, 0);
				Drawing.Set_PositionH(Asc.c_oAscRelativeFromH.Column, false, 0, false);
				Drawing.Set_PositionV(Asc.c_oAscRelativeFromV.Paragraph, false, 0, false);
			}
			this.AddToParagraph(Drawing);
			this.Select_DrawingObject(Drawing.Get_Id());
		}
		else
		{
			Item.AddInlineImage(W, H, Img, Chart, bFlow);
		}
	}
};

CDocumentContent.prototype.AddImages = function(aImages){
    if (docpostype_DrawingObjects === this.CurPos.Type)
    {
        return this.DrawingObjects.addImages(aImages);
    }
    else //if ( docpostype_Content === this.CurPos.Type )
    {
        if (true === this.Selection.Use)
            this.Remove(1, true);

        var Item = this.Content[this.CurPos.ContentPos];
        if (type_Paragraph === Item.GetType())
        {
            var Drawing, W, H;
            var ColumnSize = this.LogicDocument.GetColumnSize();
        	for(var i = 0; i < aImages.length; ++i){

                W = Math.max(1, ColumnSize.W);
                H = Math.max(1, ColumnSize.H);

                var _image = aImages[i];
                var __w = Math.max((_image.Image.width * AscCommon.g_dKoef_pix_to_mm), 1);
                var __h = Math.max((_image.Image.height * AscCommon.g_dKoef_pix_to_mm), 1);
                W      = Math.max(5, Math.min(W, __w));
                H      = Math.max(5, Math.min((W * __h / __w)));
                Drawing   = new ParaDrawing(W, H, null, this.DrawingDocument, this, null);
                var Image = this.DrawingObjects.createImage(_image.src, 0, 0, W, H);
                Image.setParent(Drawing);
                Drawing.Set_GraphicObject(Image);
                this.AddToParagraph(Drawing);
			}
        }
        else
        {
            Item.AddImages(aImages);
        }
    }
};

CDocumentContent.prototype.AddOleObject = function(W, H, nWidthPix, nHeightPix, Img, Data, sApplicationId)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.DrawingObjects.addOleObject(W, H, nWidthPix, nHeightPix, Img, Data, sApplicationId);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (true == this.Selection.Use)
			this.Remove(1, true);

		var Item = this.Content[this.CurPos.ContentPos];
		if (type_Paragraph == Item.GetType())
		{
			var Drawing = new ParaDrawing(W, H, null, this.DrawingDocument, this, null);
			var Image   = this.DrawingObjects.createOleObject(Data, sApplicationId, Img, 0, 0, W, H, nWidthPix, nHeightPix);
			Image.setParent(Drawing);
			Drawing.Set_GraphicObject(Image);

			this.AddToParagraph(Drawing);
			this.Select_DrawingObject(Drawing.Get_Id());
		}
		else
		{
			Item.AddOleObject(W, H, nWidthPix, nHeightPix, Img, Data, sApplicationId);
		}
	}
};
CDocumentContent.prototype.AddTextArt = function(nStyle)
{
	if (docpostype_DrawingObjects !== this.CurPos.Type)
	{
		var Item = this.Content[this.CurPos.ContentPos];
		if (type_Paragraph == Item.GetType())
		{
			var Drawing = new ParaDrawing(1828800 / 36000, 1828800 / 36000, null, this.DrawingDocument, this, null);
			var TextArt = this.DrawingObjects.createTextArt(nStyle, true);
			TextArt.setParent(Drawing);
			Drawing.Set_GraphicObject(TextArt);
			Drawing.Set_DrawingType(drawing_Anchor);
			Drawing.Set_WrappingType(WRAPPING_TYPE_NONE);
			Drawing.Set_BehindDoc(false);
			Drawing.Set_Distance(3.2, 0, 3.2, 0);
			Drawing.Set_PositionH(Asc.c_oAscRelativeFromH.Column, false, 0, false);
			Drawing.Set_PositionV(Asc.c_oAscRelativeFromV.Paragraph, false, 0, false);
			if (true == this.Selection.Use)
				this.Remove(1, true);
			this.AddToParagraph(Drawing);
			if (TextArt.bSelectedText)
			{
				this.Select_DrawingObject(Drawing.Get_Id());
			}
			else
			{
				var oContent = Drawing.GraphicObj.getDocContent();
				oContent.Content[0].Document_SetThisElementCurrent(false);
				this.LogicDocument.SelectAll();
			}
		}
		else
		{
			Item.AddTextArt(nStyle);
		}
	}
};
CDocumentContent.prototype.AddSignatureLine = function(oSignatureDrawing)
{
	if (docpostype_DrawingObjects !== this.CurPos.Type)
	{
        var Item = this.Content[this.CurPos.ContentPos];
        if (type_Paragraph == Item.GetType())
        {
            var Drawing = oSignatureDrawing;

            if (true == this.Selection.Use)
                this.Remove(1, true);

            this.AddToParagraph(Drawing);
            this.Select_DrawingObject(Drawing.Get_Id());
        }
        else
        {
            Item.AddSignatureLine(oSignatureDrawing);
        }
	}
};
CDocumentContent.prototype.EditChart = function(Chart)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.editChart(Chart);
	}
};
CDocumentContent.prototype.AddInlineTable = function(Cols, Rows)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.addInlineTable(Cols, Rows);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (this.CurPos.ContentPos < 0)
			return false;

		if (true === this.Selection.Use)
			this.Remove(1, true);

		// Добавляем таблицу
		var Item = this.Content[this.CurPos.ContentPos];

		// Если мы внутри параграфа, тогда разрываем его и на месте разрыва добавляем таблицу.
		// А если мы внутри таблицы, тогда добавляем таблицу внутрь текущей таблицы.
		if (type_Paragraph === Item.GetType())
		{
			// Создаем новую таблицу
			var W = 0;
			if (true === this.IsTableCellContent())
				W = this.XLimit - this.X;
			else
				W = ( this.XLimit - this.X + 2 * 1.9 );

			W = Math.max(W, Cols * 2 * 1.9);

			var Grid = [];

			for (var Index = 0; Index < Cols; Index++)
				Grid[Index] = W / Cols;

			var NewTable = new CTable(this.DrawingDocument, this, true, Rows, Cols, Grid);
			NewTable.Set_ParagraphPrOnAdd(Item);

			// Проверим позицию в текущем параграфе
			if (true === Item.IsCursorAtEnd())
			{
				// Выставляем курсор в начало таблицы
				NewTable.MoveCursorToStartPos();
				this.Internal_Content_Add(this.CurPos.ContentPos + 1, NewTable);
				this.CurPos.ContentPos++;
			}
			else
			{
				// Создаем новый параграф
				var NewParagraph = new Paragraph(this.DrawingDocument, this, this.bPresentation === true);
				Item.Split(NewParagraph);

				// Добавляем новый параграф
				this.Internal_Content_Add(this.CurPos.ContentPos + 1, NewParagraph);

				// Выставляем курсор в начало таблицы
				NewTable.MoveCursorToStartPos();
				this.Internal_Content_Add(this.CurPos.ContentPos + 1, NewTable);

				this.CurPos.ContentPos++;
			}
		}
		else
		{
			Item.AddInlineTable(Cols, Rows);
		}
	}
};
CDocumentContent.prototype.AddToParagraph = function(ParaItem, bRecalculate)
{
	if (true === this.ApplyToAll)
	{
		if (para_TextPr === ParaItem.Type)
		{
			for (var Index = 0; Index < this.Content.length; Index++)
			{
				var Item = this.Content[Index];
				Item.Set_ApplyToAll(true);
				Item.AddToParagraph(ParaItem);
				Item.Set_ApplyToAll(false);
			}
		}

		return;
	}

	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.paragraphAdd(ParaItem, bRecalculate);
	}
	else // if ( docpostype_Content === this.CurPos.Type )
	{
		if (true === this.Selection.Use)
		{
			var bAddSpace = this.LogicDocument ? this.LogicDocument.Is_WordSelection() : false;
			var Type      = ParaItem.Get_Type();
			switch (Type)
			{
				case para_Math:
				case para_NewLine:
				case para_Text:
				case para_Space:
				case para_Tab:
				case para_PageNum:
				case para_Field:
				case para_FootnoteReference:
				case para_FootnoteRef:
				case para_Separator:
				case para_ContinuationSeparator:
				{
					// Если у нас что-то заселекчено и мы вводим текст или пробел
					// и т.д., тогда сначала удаляем весь селект.
					this.Remove(1, true, false, true);

					if (true === bAddSpace)
					{
						this.AddToParagraph(new ParaSpace());
						this.MoveCursorLeft(false, false);
					}

					break;
				}
				case para_TextPr:
				{
					switch (this.Selection.Flag)
					{
						case selectionflag_Common:
						{
							// Текстовые настройки применяем ко всем параграфам, попавшим
							// в селект.
							var StartPos = this.Selection.StartPos;
							var EndPos   = this.Selection.EndPos;
							if (EndPos < StartPos)
							{
								var Temp = StartPos;
								StartPos = EndPos;
								EndPos   = Temp;
							}

							for (var Index = StartPos; Index <= EndPos; Index++)
							{
								this.Content[Index].AddToParagraph(ParaItem.Copy());
							}

							if (false != bRecalculate)
							{
								// Если в TextPr только HighLight, тогда не надо ничего пересчитывать, только перерисовываем
								if (true === ParaItem.Value.Check_NeedRecalc())
								{
									this.Recalculate();
								}
								else
								{
									// Просто перерисовываем нужные страницы
									var StartPage = this.Content[StartPos].Get_StartPage_Absolute();
									var EndPage   = this.Content[EndPos].Get_StartPage_Absolute() + this.Content[EndPos].GetPagesCount() - 1;
									this.ReDraw(StartPage, EndPage);
								}
							}

							break;
						}
						case selectionflag_Numbering:
						{
							// Текстовые настройки применяем к конкретной нумерации
							if (null == this.Selection.Data || this.Selection.Data.length <= 0)
								break;

							if (undefined != ParaItem.Value.FontFamily)
							{
								var FName  = ParaItem.Value.FontFamily.Name;
								var FIndex = ParaItem.Value.FontFamily.Index;

								ParaItem.Value.RFonts          = new CRFonts();
								ParaItem.Value.RFonts.Ascii    = {Name : FName, Index : FIndex};
								ParaItem.Value.RFonts.EastAsia = {Name : FName, Index : FIndex};
								ParaItem.Value.RFonts.HAnsi    = {Name : FName, Index : FIndex};
								ParaItem.Value.RFonts.CS       = {Name : FName, Index : FIndex};
							}

							var NumPr    = this.Content[this.Selection.Data[0]].Numbering_Get();
							var AbstrNum = this.Numbering.Get_AbstractNum(NumPr.NumId);
							AbstrNum.Apply_TextPr(NumPr.Lvl, ParaItem.Value);

							if (false != bRecalculate)
							{
								this.Recalculate();
							}

							break;
						}
					}

					return;
				}
			}
		}

		var Item     = this.Content[this.CurPos.ContentPos];
		var ItemType = Item.GetType();

		if (para_NewLine === ParaItem.Type && true === ParaItem.IsPageOrColumnBreak())
		{
			if (type_Paragraph === ItemType)
			{
				if (true === Item.IsCursorAtBegin())
				{
					this.AddNewParagraph();
					this.Content[this.CurPos.ContentPos - 1].AddToParagraph(ParaItem);
					this.Content[this.CurPos.ContentPos - 1].Clear_Formatting();
				}
				else
				{
					this.AddNewParagraph();
					this.AddNewParagraph();
					this.Content[this.CurPos.ContentPos - 1].AddToParagraph(ParaItem);
					this.Content[this.CurPos.ContentPos - 1].Clear_Formatting();
				}

				if (false != bRecalculate)
				{
					this.Recalculate();

					Item.CurPos.RealX = Item.CurPos.X;
					Item.CurPos.RealY = Item.CurPos.Y;
				}
			}
			else
			{
				// TODO: PageBreak в таблице не ставим
				return;
			}
		}
		else
		{
			Item.AddToParagraph(ParaItem);

			if (false != bRecalculate)
			{
				if (para_TextPr === ParaItem.Type && false === ParaItem.Value.Check_NeedRecalc())
				{
					// Просто перерисовываем нужные страницы
					var StartPage = Item.Get_StartPage_Absolute();
					var EndPage   = StartPage + Item.GetPagesCount() - 1;
					this.ReDraw(StartPage, EndPage);
				}
				else
				{
					this.Recalculate();
				}

				if (type_Paragraph === ItemType)
				{
					Item.RecalculateCurPos();
					Item.CurPos.RealX = Item.CurPos.X;
					Item.CurPos.RealY = Item.CurPos.Y;
				}
			}
		}
	}
};
CDocumentContent.prototype.ClearParagraphFormatting = function()
{
	if (true === this.ApplyToAll)
	{
		for (var Index = 0; Index < this.Content.length; Index++)
		{
			var Item = this.Content[Index];
			Item.Set_ApplyToAll(true);
			Item.ClearParagraphFormatting();
			Item.Set_ApplyToAll(false);
		}

		return;
	}

	if (docpostype_DrawingObjects == this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.paragraphClearFormatting();
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (true === this.Selection.Use)
		{
			if (selectionflag_Common === this.Selection.Flag)
			{
				var StartPos = this.Selection.StartPos;
				var EndPos   = this.Selection.EndPos;
				if (StartPos > EndPos)
				{
					var Temp = StartPos;
					StartPos = EndPos;
					EndPos   = Temp;
				}

				for (var Index = StartPos; Index <= EndPos; Index++)
				{
					var Item = this.Content[Index];
					Item.ClearParagraphFormatting();
				}
			}
		}
		else
		{
			var Item = this.Content[this.CurPos.ContentPos];
			Item.ClearParagraphFormatting();
		}
	}
};
CDocumentContent.prototype.Remove = function(Count, bOnlyText, bRemoveOnlySelection, bOnTextAdd)
{
	if (true === this.ApplyToAll)
	{
		this.Internal_Content_RemoveAll();
		this.Internal_Content_Add(0, this.private_CreateNewParagraph());

		this.CurPos = {
			X          : 0,
			Y          : 0,
			ContentPos : 0, // в зависимости, от параметра Type: озиция в Document.Content
			RealX      : 0, // позиция курсора, без учета расположения букв
			RealY      : 0, // это актуально для клавиш вверх и вниз
			Type       : docpostype_Content
		};

		this.Selection = {
			Start    : false,
			Use      : false,
			StartPos : 0,
			EndPos   : 0,
			Flag     : selectionflag_Common,
			Data     : null
		};

		return false;
	}

	if (undefined === bRemoveOnlySelection)
		bRemoveOnlySelection = false;

	if (undefined === bOnTextAdd)
		bOnTextAdd = false;

	if (docpostype_DrawingObjects === this.CurPos.Type)
		return this.LogicDocument.DrawingObjects.remove(Count, bOnlyText, bRemoveOnlySelection);
	else //if ( docpostype_Content === this.CurPos.Type )
		return this.private_Remove(Count, bOnlyText, bRemoveOnlySelection, bOnTextAdd);
};
CDocumentContent.prototype.GetCursorPosXY = function()
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.cursorGetPos();
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (true === this.Selection.Use)
		{
			if (selectionflag_Common === this.Selection.Flag)
			{
				return this.Content[this.Selection.EndPos].GetCursorPosXY();
			}

			return {X : 0, Y : 0};
		}
		else
		{
			return this.Content[this.CurPos.ContentPos].GetCursorPosXY();
		}
	}
};
CDocumentContent.prototype.MoveCursorLeft = function(AddToSelect, Word)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.cursorMoveLeft(AddToSelect, Word);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (this.CurPos.ContentPos < 0)
			return false;

		var ReturnValue = true;

		this.Remove_NumberingSelection();
		if (true === this.Selection.Use)
		{
			if (true === AddToSelect)
			{
				// Добавляем к селекту
				if (false === this.Content[this.Selection.EndPos].MoveCursorLeft(true, Word))
				{
					// Нужно перейти в конец предыдущего элемента
					if (0 != this.Selection.EndPos)
					{
						this.Selection.EndPos--;
						this.CurPos.ContentPos = this.Selection.EndPos;

						var Item = this.Content[this.Selection.EndPos];
						Item.MoveCursorLeftWithSelectionFromEnd(Word);
					}
					else
					{
						// Сообщаем родительскому классу, что надо выйти из данного элемента
						ReturnValue = false;
					}
				}

				// Проверяем не обнулился ли селект в последнем параграфе. Такое могло быть, если была
				// заселекчена одна буква в последнем параграфе, а мы убрали селект последним действием.
				if (this.Selection.EndPos != this.Selection.StartPos && false === this.Content[this.Selection.EndPos].IsSelectionUse())
				{
					// Такая ситуация возможна только при прямом селекте (сверху вниз), поэтому вычитаем
					this.Selection.EndPos--;
					this.CurPos.ContentPos = this.Selection.EndPos;
				}

				// Проверяем не обнулился ли селект (т.е. ничего не заселекчено)
				if (this.Selection.StartPos == this.Selection.EndPos && false === this.Content[this.Selection.StartPos].IsSelectionUse())
				{
					this.Selection.Use     = false;
					this.CurPos.ContentPos = this.Selection.EndPos;
				}
			}
			else
			{
				// Нам нужно переместить курсор в левый край селекта, и отменить весь селект
				var Start = this.Selection.StartPos;
				if (Start > this.Selection.EndPos)
					Start = this.Selection.EndPos;

				this.CurPos.ContentPos = Start;
				this.Content[this.CurPos.ContentPos].MoveCursorLeft(false, Word);

				this.RemoveSelection();
			}
		}
		else
		{
			if (true === AddToSelect)
			{
				this.Selection.Use      = true;
				this.Selection.StartPos = this.CurPos.ContentPos;
				this.Selection.EndPos   = this.CurPos.ContentPos;

				if (false === this.Content[this.CurPos.ContentPos].MoveCursorLeft(true, Word))
				{
					// Нужно перейти в конец предыдущего элемент
					if (0 != this.CurPos.ContentPos)
					{
						this.CurPos.ContentPos--;
						this.Selection.EndPos = this.CurPos.ContentPos;

						var Item = this.Content[this.CurPos.ContentPos];
						Item.MoveCursorLeftWithSelectionFromEnd(Word);
					}
					else
					{
						// Сообщаем родительскому классу, что надо выйти из данного элемента
						ReturnValue = false;
					}
				}

				// Проверяем не обнулился ли селект (т.е. ничего не заселекчено)
				if (this.Selection.StartPos == this.Selection.EndPos && false === this.Content[this.Selection.StartPos].IsSelectionUse())
				{
					this.Selection.Use     = false;
					this.CurPos.ContentPos = this.Selection.EndPos;
				}
			}
			else
			{
				if (false === this.Content[this.CurPos.ContentPos].MoveCursorLeft(false, Word))
				{
					// Нужно перейти в конец предыдущего элемент
					if (0 != this.CurPos.ContentPos)
					{
						this.CurPos.ContentPos--;
						this.Content[this.CurPos.ContentPos].MoveCursorToEndPos(false, false);
					}
					else
					{
						// Сообщаем родительскому классу, что надо выйти из данного элемента
						ReturnValue = false;
					}
				}
			}
		}

		return ReturnValue;
	}
};
CDocumentContent.prototype.MoveCursorLeftWithSelectionFromEnd = function(Word)
{
	this.RemoveSelection();

	if (this.Content.length <= 0)
		return;

	this.Selection.Use      = true;
	this.Selection.Start    = false;
	this.Selection.Data     = null;
	this.Selection.Flag     = selectionflag_Common;
	this.Selection.StartPos = this.Content.length - 1;
	this.Selection.EndPos   = this.Content.length - 1;

	this.Content[this.Content.length - 1].MoveCursorLeftWithSelectionFromEnd(Word);
};
CDocumentContent.prototype.MoveCursorRight = function(AddToSelect, Word, FromPaste)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.cursorMoveRight(AddToSelect, Word);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (this.CurPos.ContentPos < 0)
			return false;

		var ReturnValue = true;

		this.Remove_NumberingSelection();
		if (true === this.Selection.Use)
		{
			if (true === AddToSelect)
			{
				// Добавляем к селекту
				if (false === this.Content[this.Selection.EndPos].MoveCursorRight(true, Word))
				{
					// Нужно перейти в конец предыдущего элемента
					if (this.Content.length - 1 != this.Selection.EndPos)
					{
						this.Selection.EndPos++;
						this.CurPos.ContentPos = this.Selection.EndPos;

						var Item = this.Content[this.Selection.EndPos];
						Item.MoveCursorRightWithSelectionFromStart(Word);
					}
					else
					{
						// Сообщаем родительскому классу, что надо выйти из данного элемента
						ReturnValue = false;
					}
				}

				// Проверяем не обнулился ли селект в последнем параграфе. Такое могло быть, если была
				// заселекчена одна буква в последнем параграфе, а мы убрали селект последним действием.
				if (this.Selection.EndPos != this.Selection.StartPos && false === this.Content[this.Selection.EndPos].IsSelectionUse())
				{
					// Такая ситуация возможна только при обратном селекте (снизу вверх), поэтому вычитаем
					this.Selection.EndPos++;
					this.CurPos.ContentPos = this.Selection.EndPos;
				}

				// Проверяем не обнулился ли селект (т.е. ничего не заселекчено)
				if (this.Selection.StartPos == this.Selection.EndPos && false === this.Content[this.Selection.StartPos].IsSelectionUse())
				{
					this.Selection.Use     = false;
					this.CurPos.ContentPos = this.Selection.EndPos;
				}
			}
			else
			{
				// Нам нужно переместить курсор в правый край селекта, и отменить весь селект
				var End = this.Selection.EndPos;
				if (End < this.Selection.StartPos)
					End = this.Selection.StartPos;


				this.CurPos.ContentPos = End;

				if (true === this.Content[this.CurPos.ContentPos].IsSelectionToEnd() && this.CurPos.ContentPos < this.Content.length - 1)
				{
					this.CurPos.ContentPos = End + 1;
					this.Content[this.CurPos.ContentPos].MoveCursorToStartPos(false);
				}
				else
				{
					this.Content[this.CurPos.ContentPos].MoveCursorRight(false, Word);
				}

				this.RemoveSelection();
			}
		}
		else
		{
			if (true === AddToSelect)
			{
				this.Selection.Use      = true;
				this.Selection.StartPos = this.CurPos.ContentPos;
				this.Selection.EndPos   = this.CurPos.ContentPos;

				if (false === this.Content[this.CurPos.ContentPos].MoveCursorRight(true, Word))
				{
					// Нужно перейти в конец предыдущего элемента
					if (this.Content.length - 1 != this.CurPos.ContentPos)
					{
						this.CurPos.ContentPos++;
						this.Selection.EndPos = this.CurPos.ContentPos;

						var Item = this.Content[this.CurPos.ContentPos];
						Item.MoveCursorRightWithSelectionFromStart(Word);
					}
					else
					{
						// Сообщаем родительскому классу, что надо выйти из данного элемента
						ReturnValue = false;
					}
				}

				// Проверяем не обнулился ли селект (т.е. ничего не заселекчено)
				if (this.Selection.StartPos == this.Selection.EndPos && false === this.Content[this.Selection.StartPos].IsSelectionUse())
				{
					this.Selection.Use     = false;
					this.CurPos.ContentPos = this.Selection.EndPos;
				}
			}
			else
			{
				if (false === this.Content[this.CurPos.ContentPos].MoveCursorRight(false, Word))
				{
					// Нужно перейти в начало следующего элемента
					if (this.Content.length - 1 != this.CurPos.ContentPos)
					{
						this.CurPos.ContentPos++;
						this.Content[this.CurPos.ContentPos].MoveCursorToStartPos(false);
					}
					else
					{
						// Сообщаем родительскому классу, что надо выйти из данного элемента
						ReturnValue = false;
					}
				}
			}
		}

		return ReturnValue;
	}
};
CDocumentContent.prototype.MoveCursorRightWithSelectionFromStart = function(Word)
{
	this.RemoveSelection();

	if (this.Content.length <= 0)
		return;

	this.Selection.Use      = true;
	this.Selection.Start    = false;
	this.Selection.Data     = null;
	this.Selection.Flag     = selectionflag_Common;
	this.Selection.StartPos = 0;
	this.Selection.EndPos   = 0;

	this.Content[0].MoveCursorRightWithSelectionFromStart(Word);
};
CDocumentContent.prototype.MoveCursorUp = function(AddToSelect)
{
	if (docpostype_DrawingObjects == this.CurPos.Type)
		return this.LogicDocument.DrawingObjects.cursorMoveUp(AddToSelect);
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (this.CurPos.ContentPos < 0)
			return false;

		var ReturnValue = true;

		this.Remove_NumberingSelection();
		if (true === this.Selection.Use)
		{
			if (true === AddToSelect)
			{
				var SelectDirection = this.Selection.StartPos === this.Selection.EndPos ? 0 : this.Selection.StartPos < this.Selection.EndPos ? 1 : -1;

				var Item = this.Content[this.Selection.EndPos];
				if (false === Item.MoveCursorUp(true))
				{
					if (0 != this.Selection.EndPos)
					{
						var TempXY        = Item.GetCurPosXY();
						this.CurPos.RealX = TempXY.X;
						this.CurPos.RealY = TempXY.Y;

						if (1 === SelectDirection)
							Item.RemoveSelection();

						this.Selection.EndPos--;
						Item = this.Content[this.Selection.EndPos];
						Item.MoveCursorUpToLastRow(this.CurPos.RealX, this.CurPos.RealY, true);
					}
					else
					{
						// Сообщаем родительскому классу, что надо выйти из данного элемента
						ReturnValue = false;
					}
				}

				// Проверяем не обнулился ли селект (т.е. ничего не заселекчено)
				if (this.Selection.StartPos == this.Selection.EndPos && false === this.Content[this.Selection.StartPos].IsSelectionUse())
					this.Selection.Use = false;

				this.CurPos.ContentPos = this.Selection.EndPos;
			}
			else
			{
				// Мы должны переместиться на строку выше, чем начало селекта
				var Start = this.Selection.StartPos;
				if (Start > this.Selection.EndPos)
					Start = this.Selection.EndPos;

				this.CurPos.ContentPos = Start;

				var Item = this.Content[this.CurPos.ContentPos];
				if (false === this.Content[this.CurPos.ContentPos].MoveCursorUp(false))
				{
					if (0 != this.CurPos.ContentPos)
					{
						var TempXY        = Item.GetCurPosXY();
						this.CurPos.RealX = TempXY.X;
						this.CurPos.RealY = TempXY.Y;

						this.CurPos.ContentPos--;
						Item = this.Content[this.CurPos.ContentPos];
						Item.MoveCursorUpToLastRow(this.CurPos.RealX, this.CurPos.RealY, false);
					}
					else
					{
						// Сообщаем родительскому классу, что надо выйти из данного элемента
						ReturnValue = false;
					}
				}

				this.RemoveSelection();
			}
		}
		else
		{
			if (true === AddToSelect)
			{
				this.Selection.Use      = true;
				this.Selection.StartPos = this.CurPos.ContentPos;
				this.Selection.EndPos   = this.CurPos.ContentPos;

				var Item = this.Content[this.CurPos.ContentPos];
				if (false === Item.MoveCursorUp(true))
				{
					if (0 != this.CurPos.ContentPos)
					{
						var TempXY        = Item.GetCurPosXY();
						this.CurPos.RealX = TempXY.X;
						this.CurPos.RealY = TempXY.Y;

						this.CurPos.ContentPos--;
						Item = this.Content[this.CurPos.ContentPos];
						Item.MoveCursorUpToLastRow(this.CurPos.RealX, this.CurPos.RealY, true);
						this.Selection.EndPos = this.CurPos.ContentPos;
					}
					else
					{
						// Сообщаем родительскому классу, что надо выйти из данного элемента
						ReturnValue = false;
					}
				}

				// Проверяем не обнулился ли селект (т.е. ничего не заселекчено)
				if (this.Selection.StartPos == this.Selection.EndPos && false === this.Content[this.Selection.StartPos].IsSelectionUse())
					this.Selection.Use = false;

				this.CurPos.ContentPos = this.Selection.EndPos;
			}
			else
			{
				var Item = this.Content[this.CurPos.ContentPos];
				if (false === Item.MoveCursorUp(false))
				{
					if (0 != this.CurPos.ContentPos)
					{
						var TempXY        = Item.GetCurPosXY();
						this.CurPos.RealX = TempXY.X;
						this.CurPos.RealY = TempXY.Y;

						this.CurPos.ContentPos--;
						Item = this.Content[this.CurPos.ContentPos];
						Item.MoveCursorUpToLastRow(this.CurPos.RealX, this.CurPos.RealY, false);
					}
					else
					{
						// Сообщаем родительскому классу, что надо выйти из данного элемента
						ReturnValue = false;
					}
				}
			}
		}

		return ReturnValue;
	}
};
CDocumentContent.prototype.MoveCursorDown = function(AddToSelect)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
		return this.LogicDocument.DrawingObjects.cursorMoveDown(AddToSelect);
	else if (docpostype_Content === this.CurPos.Type)
	{
		if (this.CurPos.ContentPos < 0)
			return false;

		var ReturnValue = true;
		this.Remove_NumberingSelection();

		if (true === this.Selection.Use)
		{
			if (true === AddToSelect)
			{
				var SelectDirection = this.Selection.StartPos === this.Selection.EndPos ? 0 : this.Selection.StartPos < this.Selection.EndPos ? 1 : -1;

				var Item = this.Content[this.Selection.EndPos];
				if (false === Item.MoveCursorDown(true))
				{
					if (this.Content.length - 1 != this.Selection.EndPos)
					{
						var TempXY        = Item.GetCurPosXY();
						this.CurPos.RealX = TempXY.X;
						this.CurPos.RealY = TempXY.Y;

						if (-1 === SelectDirection)
							Item.RemoveSelection();

						this.Selection.EndPos++;
						Item = this.Content[this.Selection.EndPos];
						Item.MoveCursorDownToFirstRow(this.CurPos.RealX, this.CurPos.RealY, true);
					}
					else
					{
						// Сообщаем родительскому классу, что надо выйти из данного элемента
						ReturnValue = false;
					}
				}

				// Проверяем не обнулился ли селект (т.е. ничего не заселекчено)
				if (this.Selection.StartPos == this.Selection.EndPos && false === this.Content[this.Selection.StartPos].IsSelectionUse())
					this.Selection.Use = false;

				this.CurPos.ContentPos = this.Selection.EndPos;
			}
			else
			{
				// Мы должны переместиться на строку ниже, чем конец селекта
				var End = this.Selection.EndPos;
				if (End < this.Selection.StartPos)
					End = this.Selection.StartPos;

				this.CurPos.ContentPos = End;

				var Item = this.Content[this.CurPos.ContentPos];
				if (false === this.Content[this.CurPos.ContentPos].MoveCursorDown(false))
				{
					if (this.Content.length - 1 != this.CurPos.ContentPos)
					{
						var TempXY        = Item.GetCurPosXY();
						this.CurPos.RealX = TempXY.X;
						this.CurPos.RealY = TempXY.Y;

						this.CurPos.ContentPos++;
						Item = this.Content[this.CurPos.ContentPos];
						Item.MoveCursorDownToFirstRow(this.CurPos.RealX, this.CurPos.RealY, false);
					}
					else
					{
						// Сообщаем родительскому классу, что надо выйти из данного элемента
						ReturnValue = false;
					}
				}

				this.RemoveSelection();
			}
		}
		else
		{
			if (true === AddToSelect)
			{
				this.Selection.Use      = true;
				this.Selection.StartPos = this.CurPos.ContentPos;
				this.Selection.EndPos   = this.CurPos.ContentPos;

				var Item = this.Content[this.CurPos.ContentPos];
				if (false === Item.MoveCursorDown(true))
				{
					if (this.Content.length - 1 != this.CurPos.ContentPos)
					{
						var TempXY        = Item.GetCurPosXY();
						this.CurPos.RealX = TempXY.X;
						this.CurPos.RealY = TempXY.Y;

						this.CurPos.ContentPos++;
						Item = this.Content[this.CurPos.ContentPos];
						Item.MoveCursorDownToFirstRow(this.CurPos.RealX, this.CurPos.RealY, true);
						this.Selection.EndPos = this.CurPos.ContentPos;
					}
					else
					{
						// Сообщаем родительскому классу, что надо выйти из данного элемента
						ReturnValue = false;
					}
				}

				// Проверяем не обнулился ли селект (т.е. ничего не заселекчено)
				if (this.Selection.StartPos == this.Selection.EndPos && false === this.Content[this.Selection.StartPos].IsSelectionUse())
					this.Selection.Use = false;

				this.CurPos.ContentPos = this.Selection.EndPos;
			}
			else
			{
				var Item = this.Content[this.CurPos.ContentPos];

				if (false === Item.MoveCursorDown(AddToSelect))
				{
					if (this.Content.length - 1 != this.CurPos.ContentPos)
					{
						var TempXY        = Item.GetCurPosXY();
						this.CurPos.RealX = TempXY.X;
						this.CurPos.RealY = TempXY.Y;

						this.CurPos.ContentPos++;
						Item = this.Content[this.CurPos.ContentPos];
						Item.MoveCursorDownToFirstRow(this.CurPos.RealX, this.CurPos.RealY, false);
					}
					else
					{
						// Сообщаем родительскому классу, что надо выйти из данного элемента
						ReturnValue = false;
					}
				}
			}
		}

		return ReturnValue;
	}
};
CDocumentContent.prototype.MoveCursorToEndOfLine = function(AddToSelect)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
		return this.LogicDocument.DrawingObjects.cursorMoveEndOfLine(AddToSelect);
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (this.CurPos.ContentPos < 0)
			return false;

		this.Remove_NumberingSelection();
		if (true === this.Selection.Use)
		{
			if (true === AddToSelect)
			{
				var Item = this.Content[this.Selection.EndPos];
				Item.MoveCursorToEndOfLine(AddToSelect);

				// Проверяем не обнулился ли селект (т.е. ничего не заселекчено)
				if (this.Selection.StartPos == this.Selection.EndPos && false === this.Content[this.Selection.StartPos].IsSelectionUse())
				{
					this.Selection.Use     = false;
					this.CurPos.ContentPos = this.Selection.EndPos;
				}
			}
			else
			{
				var Pos                = ( this.Selection.EndPos >= this.Selection.StartPos ? this.Selection.EndPos : this.Selection.StartPos );
				this.CurPos.ContentPos = Pos;

				var Item = this.Content[Pos];
				Item.MoveCursorToEndOfLine(AddToSelect);

				this.RemoveSelection();
			}
		}
		else
		{
			if (true === AddToSelect)
			{
				this.Selection.Use      = true;
				this.Selection.StartPos = this.CurPos.ContentPos;
				this.Selection.EndPos   = this.CurPos.ContentPos;

				var Item = this.Content[this.CurPos.ContentPos];
				Item.MoveCursorToEndOfLine(AddToSelect);

				// Проверяем не обнулился ли селект (т.е. ничего не заселекчено)
				if (this.Selection.StartPos == this.Selection.EndPos && false === this.Content[this.Selection.StartPos].IsSelectionUse())
				{
					this.Selection.Use     = false;
					this.CurPos.ContentPos = this.Selection.EndPos;
				}
			}
			else
			{
				var Item = this.Content[this.CurPos.ContentPos];
				Item.MoveCursorToEndOfLine(AddToSelect);
			}
		}
	}
};
CDocumentContent.prototype.MoveCursorToStartOfLine = function(AddToSelect)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
		return this.LogicDocument.DrawingObjects.cursorMoveStartOfLine(AddToSelect);
	else // if( docpostype_Content === this.CurPos.Type )
	{
		if (this.CurPos.ContentPos < 0)
			return false;

		this.Remove_NumberingSelection();
		if (true === this.Selection.Use)
		{
			if (true === AddToSelect)
			{
				var Item = this.Content[this.Selection.EndPos];
				Item.MoveCursorToStartOfLine(AddToSelect);

				// Проверяем не обнулился ли селект (т.е. ничего не заселекчено)
				if (this.Selection.StartPos == this.Selection.EndPos && false === this.Content[this.Selection.StartPos].IsSelectionUse())
				{
					this.Selection.Use     = false;
					this.CurPos.ContentPos = this.Selection.EndPos;
				}
			}
			else
			{
				var Pos                = ( this.Selection.StartPos <= this.Selection.EndPos ? this.Selection.StartPos : this.Selection.EndPos );
				this.CurPos.ContentPos = Pos;

				var Item = this.Content[Pos];
				Item.MoveCursorToStartOfLine(AddToSelect);

				this.RemoveSelection();
			}
		}
		else
		{
			if (true === AddToSelect)
			{
				this.Selection.Use      = true;
				this.Selection.StartPos = this.CurPos.ContentPos;
				this.Selection.EndPos   = this.CurPos.ContentPos;

				var Item = this.Content[this.CurPos.ContentPos];
				Item.MoveCursorToStartOfLine(AddToSelect);

				// Проверяем не обнулился ли селект (т.е. ничего не заселекчено)
				if (this.Selection.StartPos == this.Selection.EndPos && false === this.Content[this.Selection.StartPos].IsSelectionUse())
				{
					this.Selection.Use     = false;
					this.CurPos.ContentPos = this.Selection.EndPos;
				}
			}
			else
			{
				var Item = this.Content[this.CurPos.ContentPos];
				Item.MoveCursorToStartOfLine(AddToSelect);
			}
		}
	}
};
CDocumentContent.prototype.MoveCursorToXY = function(X, Y, AddToSelect, bRemoveOldSelection, CurPage)
{
	if (this.Pages.length <= 0)
		return;

	if (undefined !== CurPage)
	{
		if (CurPage < 0)
		{
			CurPage = 0;
			Y       = 0;
		}
		else if (CurPage >= this.Pages.length)
		{
			CurPage = this.Pages.length - 1;
			Y       = this.Pages[CurPage].YLimit;
		}

		this.CurPage = CurPage;
	}

	if (false != bRemoveOldSelection)
	{
		this.Remove_NumberingSelection();
	}

	if (true === this.Selection.Use)
	{
		if (true === AddToSelect)
		{
			var oMouseEvent  = new AscCommon.CMouseEventHandler();
			oMouseEvent.Type = AscCommon.g_mouse_event_type_up;
			this.Selection_SetEnd(X, Y, this.CurPage, oMouseEvent);
		}
		else
		{
			this.RemoveSelection();

			var ContentPos         = this.Internal_GetContentPosByXY(X, Y);
			this.CurPos.ContentPos = ContentPos;
			var ElementPageIndex   = this.private_GetElementPageIndexByXY(ContentPos, X, Y, this.CurPage);
			this.Content[ContentPos].MoveCursorToXY(X, Y, false, false, ElementPageIndex);

			this.Interface_Update_ParaPr();
			this.Interface_Update_TextPr();
		}
	}
	else
	{
		if (true === AddToSelect)
		{
			this.StartSelectionFromCurPos();
			var oMouseEvent  = new AscCommon.CMouseEventHandler();
			oMouseEvent.Type = AscCommon.g_mouse_event_type_up;
			this.Selection_SetEnd(X, Y, this.CurPage, oMouseEvent);
		}
		else
		{
			var ContentPos         = this.Internal_GetContentPosByXY(X, Y);
			this.CurPos.ContentPos = ContentPos;
			var ElementPageIndex   = this.private_GetElementPageIndexByXY(ContentPos, X, Y, this.CurPage);
			this.Content[ContentPos].MoveCursorToXY(X, Y, false, false, ElementPageIndex);

			this.Interface_Update_ParaPr();
			this.Interface_Update_TextPr();
		}
	}
};
CDocumentContent.prototype.IsCursorAtBegin = function(bOnlyPara)
{
	if (undefined === bOnlyPara)
		bOnlyPara = false;

	if (true === bOnlyPara && true != this.Is_CurrentElementParagraph())
		return false;

	if (docpostype_DrawingObjects === this.CurPos.Type)
		return false;
	else if (false != this.Selection.Use || 0 != this.CurPos.ContentPos)
		return false;

	var Item = this.Content[0];
	return Item.IsCursorAtBegin();
};
CDocumentContent.prototype.IsCursorAtEnd = function()
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
		return false;
	else if (false != this.Selection.Use || 0 != this.CurPos.ContentPos)
		return false;

	var Item = this.Content[this.Content.length - 1];
	return Item.IsCursorAtEnd();
};
CDocumentContent.prototype.GetCurPosXY = function()
{
	return {X : this.CurPos.RealX, Y : this.CurPos.RealY};
};
CDocumentContent.prototype.SetCurPosXY = function(X, Y)
{
	this.CurPos.RealX = X;
	this.CurPos.RealY = Y;
};
CDocumentContent.prototype.IsSelectionUse = function()
{
	if (true == this.Selection.Use)
		return true;

	return false;
};
CDocumentContent.prototype.IsSelectionToEnd = function()
{
	if (true !== this.Selection.Use)
		return false;

	if ((this.Selection.StartPos === this.Content.length - 1 || this.Selection.EndPos === this.Content.length - 1) && true === this.Content[this.Content.length - 1].IsSelectionToEnd())
		return true;

	return false;
};
CDocumentContent.prototype.IsTextSelectionUse = function()
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
		return this.LogicDocument.DrawingObjects.isTextSelectionUse();

	return this.IsSelectionUse();
};
/**
 * Возвращаем выделенный текст, если в выделении не более 1 параграфа, и там нет картинок, нумерации страниц и т.д.
 * @param bClearText
 * @param oPr
 * @returns {?string}
 */
CDocumentContent.prototype.GetSelectedText = function(bClearText, oPr)
{
	if (true === this.ApplyToAll)
	{
		if (true === bClearText && this.Content.length <= 1)
		{
			this.Content[0].Set_ApplyToAll(true);
			var ResultText = this.Content[0].GetSelectedText(true, oPr);
			this.Content[0].Set_ApplyToAll(false);
			return ResultText;
		}
		else if (true != bClearText)
		{
			var ResultText = "";
			var Count      = this.Content.length;
			for (var Index = 0; Index < Count; Index++)
			{
				this.Content[Index].Set_ApplyToAll(true);
				ResultText += this.Content[Index].GetSelectedText(false, oPr);
				this.Content[Index].Set_ApplyToAll(false);
			}

			return ResultText;
		}
	}
	else
	{
		if (docpostype_DrawingObjects === this.CurPos.Type)
			return this.LogicDocument.DrawingObjects.getSelectedText(bClearText, oPr);

		// Либо у нас нет выделения, либо выделение внутри одного элемента
		if (docpostype_Content == this.CurPos.Type && ( ( true === this.Selection.Use && selectionflag_Common === this.Selection.Flag ) || false === this.Selection.Use ))
		{
			if (true === bClearText && (this.Selection.StartPos === this.Selection.EndPos || false === this.Selection.Use ))
			{
				var Pos = ( true == this.Selection.Use ? this.Selection.StartPos : this.CurPos.ContentPos );
				return this.Content[Pos].GetSelectedText(true, oPr);
			}
			else if (false === bClearText)
			{
				var StartPos = ( true == this.Selection.Use ? Math.min(this.Selection.StartPos, this.Selection.EndPos) : this.CurPos.ContentPos );
				var EndPos   = ( true == this.Selection.Use ? Math.max(this.Selection.StartPos, this.Selection.EndPos) : this.CurPos.ContentPos );

				var ResultText = "";

				for (var Index = StartPos; Index <= EndPos; Index++)
				{
					ResultText += this.Content[Index].GetSelectedText(false, oPr);
				}

				return ResultText;
			}
		}
	}

	return null;
};
CDocumentContent.prototype.GetSelectedElementsInfo = function(Info)
{
	if (true === this.ApplyToAll)
	{
		var Count = this.Content.length;
		if (Count > 1)
			Info.Set_MixedSelection();
		else if (Count === 1)
			this.Content[0].GetSelectedElementsInfo(Info);
	}
	else
	{
		if (docpostype_DrawingObjects === this.CurPos.Type)
			this.LogicDocument.DrawingObjects.getSelectedElementsInfo(Info);
		else //if ( docpostype_Content == this.CurPos.Type )
		{
			if (selectionflag_Numbering === this.Selection.Flag)
			{
				// Текстовые настройки применяем к конкретной нумерации
				if (!(null == this.Selection.Data || this.Selection.Data.length <= 0))
				{
					var CurPara = this.Content[this.Selection.Data[0]];
					for (var Index = 0; Index < this.Selection.Data.length; Index++)
					{
						if (this.CurPos.ContentPos === this.Selection.Data[Index])
							CurPara = this.Content[this.Selection.Data[Index]];
					}

					CurPara.GetSelectedElementsInfo(Info);
				}
			}
			else
			{
				if (true === this.Selection.Use)
				{
					if (this.Selection.StartPos != this.Selection.EndPos)
						Info.Set_MixedSelection();
					else
					{
						this.Content[this.Selection.StartPos].GetSelectedElementsInfo(Info);
					}
				}
				else
				{
					this.Content[this.CurPos.ContentPos].GetSelectedElementsInfo(Info);
				}
			}
		}
	}
};
CDocumentContent.prototype.GetSelectedContent = function(SelectedContent)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.DrawingObjects.GetSelectedContent(SelectedContent);
	}
	else
	{
		if (true !== this.Selection.Use || this.Selection.Flag !== selectionflag_Common)
			return;

		var StartPos = this.Selection.StartPos;
		var EndPos   = this.Selection.EndPos;
		if (StartPos > EndPos)
		{
			StartPos = this.Selection.EndPos;
			EndPos   = this.Selection.StartPos;
		}

		for (var Index = StartPos; Index <= EndPos; Index++)
		{
			this.Content[Index].GetSelectedContent(SelectedContent);
		}
	}
};
CDocumentContent.prototype.Insert_Content                     = function(SelectedContent, NearPos)
{
    var Para        = NearPos.Paragraph;
    var ParaNearPos = Para.Get_ParaNearestPos(NearPos);
    var LastClass   = ParaNearPos.Classes[ParaNearPos.Classes.length - 1];
    if (para_Math_Run === LastClass.Type)
    {
        var MathRun        = LastClass;
        var NewMathRun     = MathRun.Split(ParaNearPos.NearPos.ContentPos, ParaNearPos.Classes.length - 1);
        var MathContent    = ParaNearPos.Classes[ParaNearPos.Classes.length - 2];
        var MathContentPos = ParaNearPos.NearPos.ContentPos.Data[ParaNearPos.Classes.length - 2];
        var Element        = SelectedContent.Elements[0].Element;

        var InsertMathContent = null;
        for (var nPos = 0, nParaLen = Element.Content.length; nPos < nParaLen; nPos++)
        {
            if (para_Math === Element.Content[nPos].Type)
            {
                InsertMathContent = Element.Content[nPos];
                break;
            }
        }

        if (null !== InsertMathContent)
        {
            MathContent.Add_ToContent(MathContentPos + 1, NewMathRun);
            MathContent.Insert_MathContent(InsertMathContent.Root, MathContentPos + 1, true);
        }
    }
    else if (para_Run === LastClass.Type)
    {
        var Elements = SelectedContent.Elements;

        var Para     = NearPos.Paragraph;
        // Сначала найдем номер элемента, начиная с которого мы будем производить вставку
        var DstIndex = -1;
        var Count    = this.Content.length;
        for (var Index = 0; Index < Count; Index++)
        {
            if (this.Content[Index] === Para)
            {
                DstIndex = Index;
                break;
            }
        }

        if (-1 === DstIndex)
            return;

        var bNeedSelect = true;

        var Elements      = SelectedContent.Elements;
        var ElementsCount = Elements.length;
        var FirstElement  = SelectedContent.Elements[0];
        if (1 === ElementsCount && true !== FirstElement.SelectedAll && type_Paragraph === FirstElement.Element.GetType())
        {
            // Нам нужно в заданный параграф вставить выделенный текст
            var NewPara          = FirstElement.Element;
            var NewElementsCount = NewPara.Content.length - 1; // Последний ран с para_End не добавляем

            var NewElement = LastClass.Split(ParaNearPos.NearPos.ContentPos, ParaNearPos.Classes.length - 1);
            var PrevClass  = ParaNearPos.Classes[ParaNearPos.Classes.length - 2];
            var PrevPos    = ParaNearPos.NearPos.ContentPos.Data[ParaNearPos.Classes.length - 2];

            PrevClass.Add_ToContent(PrevPos + 1, NewElement);

            // TODO: Заглушка для переноса автофигур и картинок. Когда разрулим ситуацию так, чтобы когда у нас
            //       в текста была выделена автофигура выделение шло для автофигур, тогда здесь можно будет убрать.
            bNeedSelect = (true === SelectedContent.MoveDrawing ? false : true);

            for (var Index = 0; Index < NewElementsCount; Index++)
            {
                var Item = NewPara.Content[Index];
                PrevClass.Add_ToContent(PrevPos + 1 + Index, Item);

                if (true === bNeedSelect)
                    Item.SelectAll();
            }

            if (true === bNeedSelect)
            {
                PrevClass.Selection.Use      = true;
                PrevClass.Selection.StartPos = PrevPos + 1;
                PrevClass.Selection.EndPos   = PrevPos + 1 + NewElementsCount - 1;

                for (var Index = 0; Index < ParaNearPos.Classes.length - 2; Index++)
                {
                    var Class    = ParaNearPos.Classes[Index];
                    var ClassPos = ParaNearPos.NearPos.ContentPos.Data[Index];

                    Class.Selection.Use      = true;
                    Class.Selection.StartPos = ClassPos;
                    Class.Selection.EndPos   = ClassPos;
                }

                this.Selection.Use      = true;
                this.Selection.StartPos = DstIndex;
                this.Selection.EndPos   = DstIndex;
            }

            if (PrevClass.Correct_Content)
            {
                PrevClass.Correct_Content();
            }
        }
        else
        {
            var bConcatS   = ( type_Paragraph !== Elements[0].Element.GetType() ? false : true );
            var bConcatE   = ( type_Paragraph !== Elements[ElementsCount - 1].Element.GetType() || true === Elements[ElementsCount - 1].SelectedAll ? false : true );
            var ParaS      = Para;
            var ParaE      = Para;
            var ParaEIndex = DstIndex;

            // Нам надо разделить наш параграф в заданной позиции, если позиция в
            // начале или конце параграфа, тогда делить не надо
            Para.Cursor_MoveToNearPos(NearPos);
            Para.RemoveSelection();

            var bAddEmptyPara = false;

            if (true === Para.IsCursorAtEnd())
            {
                bConcatE = false;

                if (1 === ElementsCount && type_Paragraph === FirstElement.Element.GetType() && ( true === FirstElement.Element.Is_Empty() || true == FirstElement.SelectedAll ))
                {
                    bConcatS = false;

                    if (type_Paragraph !== this.Content[DstIndex].Get_Type() || true !== this.Content[DstIndex].Is_Empty())
                        DstIndex++;
                }
                else if (true === Elements[ElementsCount - 1].SelectedAll && true === bConcatS)
                    bAddEmptyPara = true;
            }
            else if (true === Para.IsCursorAtBegin())
            {
                bConcatS = false;
            }
            else
            {
                // Создаем новый параграф
                var NewParagraph = new Paragraph(this.DrawingDocument, this, this.bPresentation === true);
                Para.Split(NewParagraph);
                this.Internal_Content_Add(DstIndex + 1, NewParagraph);

                ParaE      = NewParagraph;
                ParaEIndex = DstIndex + 1;
            }

            var NewEmptyPara = null;
            if (true === bAddEmptyPara)
            {
                // Создаем новый параграф
				NewEmptyPara = new Paragraph(this.DrawingDocument, this, this.bPresentation === true);
				NewEmptyPara.Set_Pr(ParaS.Pr);
				NewEmptyPara.TextPr.Apply_TextPr(ParaS.TextPr.Value);
                this.Internal_Content_Add(DstIndex + 1, NewEmptyPara);
            }

            var StartIndex = 0;
            if (true === bConcatS)
            {
                // Вызываем так, чтобы выделить все внутренние элементы
                var _ParaS = Elements[0].Element;
                _ParaS.SelectAll();
                var _ParaSContentLen = _ParaS.Content.length;

                // Если мы присоединяем новый параграф, то и копируем все настройки параграфа (так делает Word)
                ParaS.Concat(Elements[0].Element);
                ParaS.Set_Pr(Elements[0].Element.Pr);
                ParaS.TextPr.Clear_Style();
                ParaS.TextPr.Apply_TextPr(Elements[0].Element.TextPr.Value);

                StartIndex++;

                ParaS.Selection.Use      = true;
                ParaS.Selection.StartPos = ParaS.Content.length - _ParaSContentLen;
                ParaS.Selection.EndPos   = ParaS.Content.length - 1;
            }

            var EndIndex = ElementsCount - 1;
            if (true === bConcatE)
            {
                var _ParaE    = Elements[ElementsCount - 1].Element;
                var TempCount = _ParaE.Content.length - 1;

                _ParaE.SelectAll();
                _ParaE.Concat(ParaE);
                _ParaE.Set_Pr(ParaE.Pr);

                this.Internal_Content_Add(ParaEIndex, _ParaE);
                this.Internal_Content_Remove(ParaEIndex + 1, 1);

                _ParaE.Selection.Use      = true;
                _ParaE.Selection.StartPos = 0;
                _ParaE.Selection.EndPos   = TempCount;

                EndIndex--;
            }


            for (var Index = StartIndex; Index <= EndIndex; Index++)
            {
                this.Internal_Content_Add(DstIndex + Index, Elements[Index].Element);
                this.Content[DstIndex + Index].SelectAll();
            }

			var LastPos = DstIndex + ElementsCount - 1;
			if (NewEmptyPara && NewEmptyPara === this.Content[LastPos + 1])
			{
				LastPos++;
				this.Content[LastPos].SelectAll();
			}
			else if (LastPos + 1 < this.Content.length && false === bConcatE && type_Paragraph === this.Content[LastPos + 1].Get_Type())
			{
				LastPos++;
				this.Content[LastPos].Selection.Use = true;
				this.Content[LastPos].Selection_SetBegEnd(true, true);
				this.Content[LastPos].Selection_SetBegEnd(false, true);
			}

            this.Selection.Start    = false;
            this.Selection.Use      = true;
            this.Selection.StartPos = DstIndex;
            this.Selection.EndPos   = LastPos;
			this.CurPos.ContentPos  = LastPos;
        }

        if (true === bNeedSelect)
            this.Parent.Set_CurrentElement(false, this.Get_StartPage_Absolute(), this);
        else if (null !== this.LogicDocument && docpostype_HdrFtr === this.LogicDocument.CurPos.Type)
        {
            this.Parent.Set_CurrentElement(false, this.Get_StartPage_Absolute(), this);
            var DocContent = this;
            var HdrFtr     = this.Is_HdrFtr(true);
            if (null !== HdrFtr)
                DocContent = HdrFtr.Content;

            DocContent.Set_DocPosType(docpostype_DrawingObjects);
            DocContent.Selection.Use   = true;
            DocContent.Selection.Start = false;
        }
    }
};
CDocumentContent.prototype.SetParagraphAlign = function(Align)
{
	if (true === this.ApplyToAll)
	{
		for (var Index = 0; Index < this.Content.length; Index++)
		{
			var Item = this.Content[Index];
			Item.Set_ApplyToAll(true);
			Item.SetParagraphAlign(Align);
			Item.Set_ApplyToAll(false);
		}

		return;
	}

	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.setParagraphAlign(Align);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (this.CurPos.ContentPos < 0)
			return false;

		if (true === this.Selection.Use)
		{
			var StartPos = this.Selection.StartPos;
			var EndPos   = this.Selection.EndPos;
			if (EndPos < StartPos)
			{
				var Temp = StartPos;
				StartPos = EndPos;
				EndPos   = Temp;
			}

			for (var Index = StartPos; Index <= EndPos; Index++)
			{
				var Item = this.Content[Index];
				Item.SetParagraphAlign(Align);
			}
		}
		else
		{
			this.Content[this.CurPos.ContentPos].SetParagraphAlign(Align);
		}
	}
};
CDocumentContent.prototype.SetParagraphSpacing = function(Spacing)
{
	if (true === this.ApplyToAll)
	{
		for (var Index = 0; Index < this.Content.length; Index++)
		{
			var Item = this.Content[Index];
			Item.Set_ApplyToAll(true);
			Item.SetParagraphSpacing(Spacing);
			Item.Set_ApplyToAll(false);
		}

		return;
	}

	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.setParagraphSpacing(Spacing);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (this.CurPos.ContentPos < 0)
			return false;

		if (true === this.Selection.Use)
		{
			var StartPos = this.Selection.StartPos;
			var EndPos   = this.Selection.EndPos;
			if (EndPos < StartPos)
			{
				var Temp = StartPos;
				StartPos = EndPos;
				EndPos   = Temp;
			}

			for (var Index = StartPos; Index <= EndPos; Index++)
			{
				var Item = this.Content[Index];
				Item.SetParagraphSpacing(Spacing);
			}
		}
		else
		{
			this.Content[this.CurPos.ContentPos].SetParagraphSpacing(Spacing);
		}
	}
};
CDocumentContent.prototype.SetParagraphIndent = function(Ind)
{
	if (true === this.ApplyToAll)
	{
		for (var Index = 0; Index < this.Content.length; Index++)
		{
			var Item = this.Content[Index];
			Item.Set_ApplyToAll(true);
			Item.SetParagraphIndent(Ind);
			Item.Set_ApplyToAll(false);
		}

		return;
	}

	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.setParagraphIndent(Ind);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (this.CurPos.ContentPos < 0)
			return false;

		if (true === this.Selection.Use)
		{
			var StartPos = this.Selection.StartPos;
			var EndPos   = this.Selection.EndPos;
			if (EndPos < StartPos)
			{
				var Temp = StartPos;
				StartPos = EndPos;
				EndPos   = Temp;
			}

			for (var Index = StartPos; Index <= EndPos; Index++)
			{
				var Item = this.Content[Index];
				Item.SetParagraphIndent(Ind);
			}
		}
		else
		{
			var Item = this.Content[this.CurPos.ContentPos];
			Item.SetParagraphIndent(Ind);
		}
	}
};
CDocumentContent.prototype.SetParagraphNumbering = function(NumInfo)
{
	if (true === this.ApplyToAll)
	{
		// TODO : реализовать
		return;
	}

	if (docpostype_DrawingObjects === this.CurPos.Type)
		return this.LogicDocument.DrawingObjects.setParagraphNumbering(NumInfo);
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (this.CurPos.ContentPos < 0)
			return false;

		if (true === this.Selection.Use && selectionflag_Numbering !== this.Selection.Flag)
		{
			if (this.Selection.StartPos === this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType())
			{
				this.Content[this.Selection.StartPos].SetParagraphNumbering(NumInfo);
				return true;
			}

			var StartPos = this.Selection.StartPos;
			var EndPos   = this.Selection.EndPos;
			if (EndPos < StartPos)
			{
				var Temp = StartPos;
				StartPos = EndPos;
				EndPos   = Temp;
			}

			if (NumInfo.SubType < 0)
			{
				// Убираем список из всех параграфов попавших в селект
				for (var Index = StartPos; Index <= EndPos; Index++)
				{
					if (type_Paragraph == this.Content[Index].GetType())
						this.Content[Index].Numbering_Remove();
					else
						this.Content[Index].SetParagraphNumbering(NumInfo);
				}
			}
			else
			{
				switch (NumInfo.Type)
				{
					case 0: // Bullet
					{
						if (0 === NumInfo.SubType)
						{
							// Если мы просто нажимаем добавить маркированный список, тогда мы пытаемся
							// присоединить его к списку предыдушего параграфа (если у предыдущего параграфа
							// есть список, и этот список маркированный)

							// Проверяем предыдущий элемент
							var Prev   = this.Content[StartPos - 1];
							var NumId  = null;
							var NumLvl = 0;

							if ("undefined" != typeof(Prev) && null != Prev && type_Paragraph === Prev.GetType())
							{
								var PrevNumPr = Prev.Numbering_Get();
								if (undefined != PrevNumPr && true === this.Numbering.Check_Format(PrevNumPr.NumId, PrevNumPr.Lvl, numbering_numfmt_Bullet))
								{
									NumId  = PrevNumPr.NumId;
									NumLvl = PrevNumPr.Lvl;
								}
							}

							// Предыдущий параграф не содержит списка, либо список не того формата
							// создаем новую нумерацию (стандартную маркированный список)
							if (null === NumId)
							{
								NumId  = this.Numbering.Create_AbstractNum();
								NumLvl = 0;

								this.Numbering.Get_AbstractNum(NumId).Create_Default_Bullet();
							}

							// Параграфы, которые не содержали списка у них уровень выставляем NumLvl,
							// а у тех которые содержали, мы уровень не меняем
							for (var Index = StartPos; Index <= EndPos; Index++)
							{
								var OldNumPr = null;

								if (type_Paragraph === this.Content[Index].GetType())
								{
									if (undefined != ( OldNumPr = this.Content[Index].Numbering_Get() ))
										this.Content[Index].Numbering_Add(NumId, OldNumPr.Lvl);
									else
										this.Content[Index].Numbering_Add(NumId, NumLvl);
								}
								else
								{
									this.Content[Index].SetParagraphNumbering(NumInfo);
								}
							}
						}
						else
						{
							// Для начала пробежимся по отмеченным параграфам и узнаем, есть ли
							// среди них параграфы со списками разных уровней.
							var bDiffLvl = false;
							var bDiffId  = false;
							var PrevLvl  = null;
							var PrevId   = null;
							for (var Index = StartPos; Index <= EndPos; Index++)
							{
								var NumPr = null;
								if (type_Paragraph === this.Content[Index].GetType() && undefined != ( NumPr = this.Content[Index].Numbering_Get() ))
								{
									if (null === PrevLvl)
										PrevLvl = NumPr.Lvl;

									if (null === PrevId)
										PrevId = NumPr.NumId;

									if (PrevId != NumPr.NumId)
										bDiffId = true;

									if (PrevLvl != NumPr.Lvl)
									{
										bDiffLvl = true;
										break;
									}
								}
								else if (( type_Paragraph === this.Content[Index].GetType() && undefined === NumPr ) || type_Paragraph !== this.Content[Index].GetType())
								{
									bDiffLvl = true;
									break;
								}
							}

							// 1. Если у нас есть параграфы со списками разных уровней, тогда мы
							//    делаем стандартный маркированный список, у которого первый(нулевой)
							//    уровень изменен на тот который задан через NumInfo.SubType
							// 2. Если все параграфы содержат списки одного уровня.
							//    2.1 Если у всех списков одинаковый Id, тогда мы создаем
							//        копию текущего списка и меняем в нем текущий уровень
							//        на тот, который задан через NumInfo.SubType
							//    2.2 Если у списков разные Id, тогда мы создаем стандартный
							//        маркированный список с измененным уровнем (равным текущему),
							//        на тот, который прописан в NumInfo.Subtype

							var LvlText   = "";
							var LvlTextPr = new CTextPr();
							LvlTextPr.RFonts.Set_All("Times New Roman", -1);

							switch (NumInfo.SubType)
							{
								case 1:
								{
									LvlText = String.fromCharCode(0x00B7);
									LvlTextPr.RFonts.Set_All("Symbol", -1);
									break;
								}
								case 2:
								{
									LvlText = "o";
									LvlTextPr.RFonts.Set_All("Courier New", -1);
									break;
								}
								case 3:
								{
									LvlText = String.fromCharCode(0x00A7);
									LvlTextPr.RFonts.Set_All("Wingdings", -1);
									break;
								}
								case 4:
								{
									LvlText = String.fromCharCode(0x0076);
									LvlTextPr.RFonts.Set_All("Wingdings", -1);
									break;
								}
								case 5:
								{
									LvlText = String.fromCharCode(0x00D8);
									LvlTextPr.RFonts.Set_All("Wingdings", -1);
									break;
								}
								case 6:
								{
									LvlText = String.fromCharCode(0x00FC);
									LvlTextPr.RFonts.Set_All("Wingdings", -1);
									break;
								}
								case 7:
								{
									LvlText = String.fromCharCode(0x00A8);
									LvlTextPr.RFonts.Set_All("Symbol", -1);

									break;
								}
							}

							var NumId = null;
							if (true === bDiffLvl)
							{
								NumId           = this.Numbering.Create_AbstractNum();
								var AbstractNum = this.Numbering.Get_AbstractNum(NumId);
								AbstractNum.Create_Default_Bullet();
								AbstractNum.Set_Lvl_Bullet(0, LvlText, LvlTextPr);
							}
							else if (true === bDiffId || true != this.Numbering.Check_Format(PrevId, PrevLvl, numbering_numfmt_Bullet))
							{
								NumId           = this.Numbering.Create_AbstractNum();
								var AbstractNum = this.Numbering.Get_AbstractNum(NumId);
								AbstractNum.Create_Default_Bullet();
								AbstractNum.Set_Lvl_Bullet(PrevLvl, LvlText, LvlTextPr);
							}
							else
							{
								NumId              = this.Numbering.Create_AbstractNum();
								var OldAbstractNum = this.Numbering.Get_AbstractNum(PrevId);
								var NewAbstractNum = this.Numbering.Get_AbstractNum(NumId);

								NewAbstractNum.Copy(OldAbstractNum);
								NewAbstractNum.Set_Lvl_Bullet(PrevLvl, LvlText, LvlTextPr);
							}

							// Параграфы, которые не содержали списка у них уровень выставляем 0,
							// а у тех которые содержали, мы уровень не меняем
							for (var Index = StartPos; Index <= EndPos; Index++)
							{
								var OldNumPr = null;
								if (type_Paragraph === this.Content[Index].GetType())
								{
									if (undefined != ( OldNumPr = this.Content[Index].Numbering_Get() ))
										this.Content[Index].Numbering_Add(NumId, OldNumPr.Lvl);
									else
										this.Content[Index].Numbering_Add(NumId, 0);
								}
								else
								{
									this.Content[Index].SetParagraphNumbering(NumInfo);
								}
							}
						}

						break;
					}
					case 1: // Numbered
					{
						if (0 === NumInfo.SubType)
						{
							// Если мы просто нажимаем добавить нумерованный список, тогда мы пытаемся
							// присоединить его к списку предыдушего параграфа (если у предыдущего параграфа
							// есть список, и этот список нумерованный)

							// Проверяем предыдущий элемент
							var Prev   = this.Content[StartPos - 1];
							var NumId  = null;
							var NumLvl = 0;

							if ("undefined" != typeof(Prev) && null != Prev && type_Paragraph === Prev.GetType())
							{
								var PrevNumPr = Prev.Numbering_Get();
								if (undefined != PrevNumPr && true === this.Numbering.Check_Format(PrevNumPr.NumId, PrevNumPr.Lvl, numbering_numfmt_Decimal))
								{
									NumId  = PrevNumPr.NumId;
									NumLvl = PrevNumPr.Lvl;
								}
							}

							// Предыдущий параграф не содержит списка, либо список не того формата
							// создаем новую нумерацию (стандартную маркированный список)
							if (null === NumId)
							{
								// Посмотрим на следующий параграф, возможно у него есть нумерованный список.
								var Next = this.Content[StartPos + 1];
								if (StartPos === EndPos && undefined !== Next && null !== Next && type_Paragraph === Next.GetType())
								{
									var NextNumPr = Next.Numbering_Get();
									if (undefined !== NextNumPr && true === this.Numbering.Check_Format(NextNumPr.NumId, NextNumPr.Lvl, numbering_numfmt_Decimal))
									{
										NumId  = NextNumPr.NumId;
										NumLvl = NextNumPr.Lvl;
									}
								}

								if (null === NumId)
								{
									NumId  = this.Numbering.Create_AbstractNum();
									NumLvl = 0;

									this.Numbering.Get_AbstractNum(NumId).Create_Default_Numbered();
								}
							}

							// Параграфы, которые не содержали списка у них уровень выставляем NumLvl,
							// а у тех которые содержали, мы уровень не меняем
							for (var Index = StartPos; Index <= EndPos; Index++)
							{
								var OldNumPr = null;

								if (type_Paragraph === this.Content[Index].GetType())
								{
									if (undefined != ( OldNumPr = this.Content[Index].Numbering_Get() ))
										this.Content[Index].Numbering_Add(NumId, OldNumPr.Lvl);
									else
										this.Content[Index].Numbering_Add(NumId, NumLvl);
								}
								else
								{
									this.Content[Index].SetParagraphNumbering(NumInfo);
								}
							}
						}
						else
						{
							// Для начала пробежимся по отмеченным параграфам и узнаем, есть ли
							// среди них параграфы со списками разных уровней.
							var bDiffLvl = false;
							var bDiffId  = false;
							var PrevLvl  = null;
							var PrevId   = null;
							for (var Index = StartPos; Index <= EndPos; Index++)
							{
								var NumPr = null;
								if (type_Paragraph === this.Content[Index].GetType() && undefined != ( NumPr = this.Content[Index].Numbering_Get() ))
								{
									if (null === PrevLvl)
										PrevLvl = NumPr.Lvl;

									if (null === PrevId)
										PrevId = NumPr.NumId;

									if (PrevId != NumPr.NumId)
										bDiffId = true;

									if (PrevLvl != NumPr.Lvl)
									{
										bDiffLvl = true;
										break;
									}
								}
								else if (( type_Paragraph === this.Content[Index].GetType() && undefined === NumPr ) || type_Paragraph !== this.Content[Index].GetType())
								{
									bDiffLvl = true;
									break;
								}
							}

							// 1. Если у нас есть параграфы со списками разных уровней, тогда мы
							//    делаем стандартный нумерованный список, у которого первый(нулевой)
							//    уровень изменен на тот который задан через NumInfo.SubType
							// 2. Если все параграфы содержат списки одного уровня.
							//    2.1 Если у всех списков одинаковый Id, тогда мы создаем
							//        копию текущего списка и меняем в нем текущий уровень
							//        на тот, который задан через NumInfo.SubType
							//    2.2 Если у списков разные Id, тогда мы создаем стандартный
							//        нумерованный список с измененным уровнем (равным текущему),
							//        на тот, который прописан в NumInfo.Subtype

							var AbstractNum = null;
							var ChangeLvl   = 0;

							var NumId = null;
							if (true === bDiffLvl)
							{
								NumId       = this.Numbering.Create_AbstractNum();
								AbstractNum = this.Numbering.Get_AbstractNum(NumId);
								AbstractNum.Create_Default_Numbered();
								ChangeLvl = 0;
							}
							else if (true === bDiffId || true != this.Numbering.Check_Format(PrevId, PrevLvl, numbering_numfmt_Decimal))
							{
								NumId       = this.Numbering.Create_AbstractNum();
								AbstractNum = this.Numbering.Get_AbstractNum(NumId);
								AbstractNum.Create_Default_Numbered();
								ChangeLvl = PrevLvl;
							}
							else
							{
								NumId              = this.Numbering.Create_AbstractNum();
								var OldAbstractNum = this.Numbering.Get_AbstractNum(PrevId);
								AbstractNum        = this.Numbering.Get_AbstractNum(NumId);
								AbstractNum.Copy(OldAbstractNum);
								ChangeLvl = PrevLvl;
							}

							switch (NumInfo.SubType)
							{
								case 1:
								{
									AbstractNum.Set_Lvl_Numbered_2(ChangeLvl);
									break;
								}
								case 2:
								{
									AbstractNum.Set_Lvl_Numbered_1(ChangeLvl);
									break;
								}
								case 3:
								{
									AbstractNum.Set_Lvl_Numbered_5(ChangeLvl);
									break;
								}
								case 4:
								{
									AbstractNum.Set_Lvl_Numbered_6(ChangeLvl);
									break;
								}
								case 5:
								{
									AbstractNum.Set_Lvl_Numbered_7(ChangeLvl);
									break;
								}
								case 6:
								{
									AbstractNum.Set_Lvl_Numbered_8(ChangeLvl);
									break;
								}
								case 7:
								{
									AbstractNum.Set_Lvl_Numbered_9(ChangeLvl);
									break;
								}
							}

							// Параграфы, которые не содержали списка у них уровень выставляем 0,
							// а у тех которые содержали, мы уровень не меняем
							for (var Index = StartPos; Index <= EndPos; Index++)
							{
								var OldNumPr = null;

								if (type_Paragraph === this.Content[Index].GetType())
								{
									if (undefined != ( OldNumPr = this.Content[Index].Numbering_Get() ))
										this.Content[Index].Numbering_Add(NumId, OldNumPr.Lvl);
									else
										this.Content[Index].Numbering_Add(NumId, 0);
								}
								else
								{
									this.Content[Index].SetParagraphNumbering(NumInfo);
								}
							}
						}

						break;
					}
					case 2: // Multilevel
					{
						// Создаем новый многоуровневый список, соответствующий NumInfo.SubType
						var NumId       = this.Numbering.Create_AbstractNum();
						var AbstractNum = this.Numbering.Get_AbstractNum(NumId);

						switch (NumInfo.SubType)
						{
							case 1:
							{
								AbstractNum.Create_Default_Multilevel_1();
								break;
							}
							case 2:
							{
								AbstractNum.Create_Default_Multilevel_2();
								break;
							}
							case 3:
							{
								AbstractNum.Create_Default_Multilevel_3();
								break;
							}
						}

						// Параграфы, которые не содержали списка у них уровень выставляем 0,
						// а у тех которые содержали, мы уровень не меняем
						for (var Index = StartPos; Index <= EndPos; Index++)
						{
							var OldNumPr = null;
							if (type_Paragraph === this.Content[Index].GetType())
							{
								if (undefined != ( OldNumPr = this.Content[Index].Numbering_Get() ))
									this.Content[Index].Numbering_Add(NumId, OldNumPr.Lvl);
								else
									this.Content[Index].Numbering_Add(NumId, 0);
							}
							else
							{
								this.Content[Index].SetParagraphNumbering(NumInfo);
							}
						}

						break;
					}
				}
			}

			this.Recalculate();
			return;
		}

		var Item = this.Content[this.CurPos.ContentPos];
		if (type_Paragraph == Item.GetType())
		{
			if (NumInfo.SubType < 0)
			{
				// Убираем список у параграфа
				Item.Numbering_Remove();
				if (selectionflag_Numbering === this.Selection.Flag)
					Item.Document_SetThisElementCurrent(true);
			}
			else
			{
				if (selectionflag_Numbering === this.Selection.Flag && 0 === NumInfo.SubType)
					NumInfo.SubType = 1;

				switch (NumInfo.Type)
				{
					case 0: // Bullet
					{
						if (0 === NumInfo.SubType)
						{
							var NumPr = Item.Numbering_Get();
							if (undefined != ( NumPr = Item.Numbering_Get() ))
							{
								var AbstractNum = this.Numbering.Get_AbstractNum(NumPr.NumId);
								if (false === this.Numbering.Check_Format(NumPr.NumId, NumPr.Lvl, numbering_numfmt_Bullet))
								{
									AbstractNum.Create_Default_Bullet();
								}
							}
							else
							{
								// Если мы просто нажимаем добавить маркированный список, тогда мы пытаемся
								// присоединить его к списку предыдушего параграфа (если у предыдущего параграфа
								// есть список, и этот список маркированный)

								// Проверяем предыдущий элемент
								var Prev   = this.Content[StartPos - 1];
								var NumId  = null;
								var NumLvl = 0;

								if ("undefined" != typeof(Prev) && null != Prev && type_Paragraph === Prev.GetType())
								{
									var PrevNumPr = Prev.Numbering_Get();
									if (undefined != PrevNumPr && true === this.Numbering.Check_Format(PrevNumPr.NumId, PrevNumPr.Lvl, numbering_numfmt_Bullet))
									{
										NumId  = PrevNumPr.NumId;
										NumLvl = PrevNumPr.Lvl;
									}
								}

								// Предыдущий параграф не содержит списка, либо список не того формата
								// создаем новую нумерацию (стандартную маркированный список)
								if (null === NumId)
								{
									NumId  = this.Numbering.Create_AbstractNum();
									NumLvl = 0;

									this.Numbering.Get_AbstractNum(NumId).Create_Default_Bullet();
								}

								var OldNumPr = Item.Numbering_Get();
								if (undefined != OldNumPr)
									Item.Numbering_Add(NumId, OldNumPr.Lvl);
								else
									Item.Numbering_Add(NumId, NumLvl);
							}
						}
						else
						{
							// 1. Если данный параграф не содержит списка, тогда мы создаем новый
							//    список, и добавляем его к данному параграфу
							// 2. Если данный параграф содержит список, тогда мы у данного списка
							//    изменяем уровень(соответствующий данному параграфу) на тот,
							//    который определен в NumInfo.Subtype

							var LvlText   = "";
							var LvlTextPr = new CTextPr();
							LvlTextPr.RFonts.Set_All("Times New Roman", -1);

							switch (NumInfo.SubType)
							{
								case 1:
								{
									LvlText = String.fromCharCode(0x00B7);
									LvlTextPr.RFonts.Set_All("Symbol", -1);
									break;
								}
								case 2:
								{
									LvlText = "o";
									LvlTextPr.RFonts.Set_All("Courier New", -1);
									break;
								}
								case 3:
								{
									LvlText = String.fromCharCode(0x00A7);
									LvlTextPr.RFonts.Set_All("Wingdings", -1);
									break;
								}
								case 4:
								{
									LvlText = String.fromCharCode(0x0076);
									LvlTextPr.RFonts.Set_All("Wingdings", -1);
									break;
								}
								case 5:
								{
									LvlText = String.fromCharCode(0x00D8);
									LvlTextPr.RFonts.Set_All("Wingdings", -1);
									break;
								}
								case 6:
								{
									LvlText = String.fromCharCode(0x00FC);
									LvlTextPr.RFonts.Set_All("Wingdings", -1);
									break;
								}
								case 7:
								{
									LvlText = String.fromCharCode(0x00A8);
									LvlTextPr.RFonts.Set_All("Symbol", -1);
									break;
								}
							}


							var NumPr = null;
							if (undefined != ( NumPr = Item.Numbering_Get() ))
							{
								var AbstractNum = this.Numbering.Get_AbstractNum(NumPr.NumId);
								AbstractNum.Set_Lvl_Bullet(NumPr.Lvl, LvlText, LvlTextPr);
							}
							else
							{
								var NumId       = this.Numbering.Create_AbstractNum();
								var AbstractNum = this.Numbering.Get_AbstractNum(NumId);
								AbstractNum.Create_Default_Bullet();
								AbstractNum.Set_Lvl_Bullet(0, LvlText, LvlTextPr);

								Item.Numbering_Add(NumId, 0);
							}
						}

						break;
					}
					case 1: // Numbered
					{
						if (0 === NumInfo.SubType)
						{
							var NumPr = Item.Numbering_Get();
							if (undefined != ( NumPr = Item.Numbering_Get() ))
							{
								var AbstractNum = this.Numbering.Get_AbstractNum(NumPr.NumId);
								if (false === this.Numbering.Check_Format(NumPr.NumId, NumPr.Lvl, numbering_numfmt_Decimal))
								{
									AbstractNum.Create_Default_Numbered();
								}
							}
							else
							{
								// Если мы просто нажимаем добавить нумерованный список, тогда мы пытаемся
								// присоединить его к списку предыдушего параграфа (если у предыдущего параграфа
								// есть список, и этот список нумерованный)

								// Проверяем предыдущий элемент
								var Prev   = this.Content[StartPos - 1];
								var NumId  = null;
								var NumLvl = 0;

								if ("undefined" != typeof(Prev) && null != Prev && type_Paragraph === Prev.GetType())
								{
									var PrevNumPr = Prev.Numbering_Get();
									if (undefined != PrevNumPr && true === this.Numbering.Check_Format(PrevNumPr.NumId, PrevNumPr.Lvl, numbering_numfmt_Decimal))
									{
										NumId  = PrevNumPr.NumId;
										NumLvl = PrevNumPr.Lvl;
									}
								}

								// Предыдущий параграф не содержит списка, либо список не того формата
								// создаем новую нумерацию (стандартную маркированный список)
								if (null === NumId)
								{
									// Посмотрим на следующий параграф, возможно у него есть нумерованный список.
									var Next = this.Content[this.CurPos.ContentPos + 1];
									if (undefined !== Next && null !== Next && type_Paragraph === Next.GetType())
									{
										var NextNumPr = Next.Numbering_Get();
										if (undefined !== NextNumPr && true === this.Numbering.Check_Format(NextNumPr.NumId, NextNumPr.Lvl, numbering_numfmt_Decimal))
										{
											NumId  = NextNumPr.NumId;
											NumLvl = NextNumPr.Lvl;
										}
									}

									if (null === NumId)
									{
										NumId  = this.Numbering.Create_AbstractNum();
										NumLvl = 0;

										this.Numbering.Get_AbstractNum(NumId).Create_Default_Numbered();
									}
								}

								var OldNumPr = Item.Numbering_Get();
								if (undefined != ( OldNumPr ))
									Item.Numbering_Add(NumId, OldNumPr.Lvl);
								else
									Item.Numbering_Add(NumId, NumLvl);
							}
						}
						else
						{
							// 1. Если данный параграф не содержит списка, тогда мы создаем новый
							//    список, и добавляем его к данному параграфу
							// 2. Если данный параграф содержит список, тогда мы у данного списка
							//    изменяем уровень(соответствующий данному параграфу) на тот,
							//    который определен в NumInfo.Subtype

							var NumPr       = null;
							var AbstractNum = null;
							var ChangeLvl   = 0;
							if (undefined != ( NumPr = Item.Numbering_Get() ))
							{
								AbstractNum = this.Numbering.Get_AbstractNum(NumPr.NumId);
								ChangeLvl   = NumPr.Lvl;
							}
							else
							{
								var NumId   = this.Numbering.Create_AbstractNum();
								AbstractNum = this.Numbering.Get_AbstractNum(NumId);
								AbstractNum.Create_Default_Numbered();
								ChangeLvl = 0;
							}

							switch (NumInfo.SubType)
							{
								case 1:
								{
									AbstractNum.Set_Lvl_Numbered_2(ChangeLvl);
									break;
								}
								case 2:
								{
									AbstractNum.Set_Lvl_Numbered_1(ChangeLvl);
									break;
								}
								case 3:
								{
									AbstractNum.Set_Lvl_Numbered_5(ChangeLvl);
									break;
								}
								case 4:
								{
									AbstractNum.Set_Lvl_Numbered_6(ChangeLvl);
									break;
								}
								case 5:
								{
									AbstractNum.Set_Lvl_Numbered_7(ChangeLvl);
									break;
								}
								case 6:
								{
									AbstractNum.Set_Lvl_Numbered_8(ChangeLvl);
									break;
								}
								case 7:
								{
									AbstractNum.Set_Lvl_Numbered_9(ChangeLvl);
									break;
								}
							}


							if (!NumPr)
								Item.Numbering_Add(NumId, 0);
						}

						break;
					}

					case 2: // Multilevel
					{
						// 1. Если у параграфа нет списка, тогда создаем новый список,
						//    и добавляем его к параграфу.
						// 2. Если у параграфа есть список, тогда изменяем этот многоуровневый
						//    список на заданный через NumInfo.SubType.

						var NumId       = null;
						var NumPr       = null;
						var AbstractNum = null;
						if (undefined != ( NumPr = Item.Numbering_Get() ))
						{
							AbstractNum = this.Numbering.Get_AbstractNum(NumPr.NumId);
						}
						else
						{
							NumId       = this.Numbering.Create_AbstractNum();
							AbstractNum = this.Numbering.Get_AbstractNum(NumId);
						}

						switch (NumInfo.SubType)
						{
							case 1:
							{
								AbstractNum.Create_Default_Multilevel_1();
								break;
							}
							case 2:
							{
								AbstractNum.Create_Default_Multilevel_2();
								break;
							}
							case 3:
							{
								AbstractNum.Create_Default_Multilevel_3();
								break;
							}
						}

						if (!NumPr)
							Item.Numbering_Add(NumId, 0);

						break;
					}
				}
			}
		}
		else
		{
			Item.SetParagraphNumbering(NumInfo);
		}
	}
};
CDocumentContent.prototype.Set_ParagraphPresentationNumbering = function(Bullet)
{
    if (true === this.ApplyToAll)
    {
        for (var Index = 0; Index < this.Content.length; Index++)
        {
            this.Content[Index].Add_PresentationNumbering(Bullet);
        }
        return;
    }

    if (this.CurPos.ContentPos < 0)
        return false;

    if (true === this.Selection.Use)
    {
        var StartPos = this.Selection.StartPos;
        var EndPos   = this.Selection.EndPos;
        if (EndPos < StartPos)
        {
            var Temp = StartPos;
            StartPos = EndPos;
            EndPos   = Temp;
        }

        for (var Index = StartPos; Index <= EndPos; Index++)
        {
            this.Content[Index].Add_PresentationNumbering(Bullet);
        }
        this.Recalculate();
        return;
    }
    this.Content[this.CurPos.ContentPos].Add_PresentationNumbering(Bullet);
    this.Recalculate();
};
CDocumentContent.prototype.Can_IncreaseParagraphLevel         = function(bIncrease)
{
    if (true === this.ApplyToAll)
    {
        for (var Index = 0; Index < this.Content.length; Index++)
        {
            if (!this.Content[Index].Can_IncreaseLevel(bIncrease))
                return false;
        }
        return true;
    }

    if (this.CurPos.ContentPos < 0)
        return false;

    if (true === this.Selection.Use)
    {
        var StartPos = this.Selection.StartPos;
        var EndPos   = this.Selection.EndPos;
        if (EndPos < StartPos)
        {
            var Temp = StartPos;
            StartPos = EndPos;
            EndPos   = Temp;
        }

        for (var Index = StartPos; Index <= EndPos; Index++)
        {
            if (!this.Content[Index].Can_IncreaseLevel(bIncrease))
            {
                return false;
            }
        }

        return true;
    }
    return this.Content[this.CurPos.ContentPos].Can_IncreaseLevel(bIncrease);
};
CDocumentContent.prototype.Increase_ParagraphLevel            = function(bIncrease)
{
    if (!this.Can_IncreaseParagraphLevel(bIncrease))
        return;
    if (true === this.ApplyToAll)
    {
        for (var Index = 0; Index < this.Content.length; Index++)
        {
            this.Content[Index].Increase_Level(bIncrease);
        }
        return;
    }

    if (this.CurPos.ContentPos < 0)
        return false;

    if (true === this.Selection.Use)
    {
        var StartPos = this.Selection.StartPos;
        var EndPos   = this.Selection.EndPos;
        if (EndPos < StartPos)
        {
            var Temp = StartPos;
            StartPos = EndPos;
            EndPos   = Temp;
        }

        for (var Index = StartPos; Index <= EndPos; Index++)
        {
            this.Content[Index].Increase_Level(bIncrease);
        }
        this.Recalculate();
        return;
    }
    this.Content[this.CurPos.ContentPos].Increase_Level(bIncrease);
    this.Recalculate();
};
CDocumentContent.prototype.SetParagraphShd = function(Shd)
{
	if (true === this.ApplyToAll)
	{
		for (var Index = 0; Index < this.Content.length; Index++)
		{
			// При изменении цвета фона параграфа, не надо ничего пересчитывать
			var Item = this.Content[Index];
			Item.Set_ApplyToAll(true);
			Item.SetParagraphShd(Shd);
			Item.Set_ApplyToAll(false);
		}

		return;
	}

	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.setParagraphShd(Shd);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (this.CurPos.ContentPos < 0)
			return false;

		if (true === this.Selection.Use)
		{
			var StartPos = this.Selection.StartPos;
			var EndPos   = this.Selection.EndPos;

			if (undefined !== this.LogicDocument && true === this.LogicDocument.UseTextShd && StartPos === EndPos && type_Paragraph === this.Content[StartPos].GetType() && false === this.Content[StartPos].Selection_CheckParaEnd() && selectionflag_Common === this.Selection.Flag)
			{
				this.AddToParagraph(new ParaTextPr({Shd : Shd}));
			}
			else
			{
				if (EndPos < StartPos)
				{
					var Temp = StartPos;
					StartPos = EndPos;
					EndPos   = Temp;
				}

				for (var Index = StartPos; Index <= EndPos; Index++)
				{
					var Item = this.Content[Index];
					Item.SetParagraphShd(Shd);
				}
			}
		}
		else
		{
			var Item = this.Content[this.CurPos.ContentPos];
			Item.SetParagraphShd(Shd);
		}
	}
};
CDocumentContent.prototype.SetParagraphStyle = function(Name)
{
	if (true === this.ApplyToAll)
	{
		for (var Index = 0; Index < this.Content.length; Index++)
		{
			var Item = this.Content[Index];
			Item.Set_ApplyToAll(true);
			Item.SetParagraphStyle(Name);
			Item.Set_ApplyToAll(false);
		}

		return;
	}

	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.setParagraphStyle(Name);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (this.CurPos.ContentPos < 0)
			return false;

		if (true === this.Selection.Use)
		{
			var StartPos = this.Selection.StartPos;
			var EndPos   = this.Selection.EndPos;
			if (EndPos < StartPos)
			{
				var Temp = StartPos;
				StartPos = EndPos;
				EndPos   = Temp;
			}

			if (selectionflag_Numbering === this.Selection.Flag)
				this.Remove_NumberingSelection();

			for (var Index = StartPos; Index <= EndPos; Index++)
			{
				var Item = this.Content[Index];
				Item.SetParagraphStyle(Name);
			}
		}
		else
		{
			var Item = this.Content[this.CurPos.ContentPos];
			Item.SetParagraphStyle(Name);
		}
	}
};
CDocumentContent.prototype.SetParagraphTabs = function(Tabs)
{
	if (true === this.ApplyToAll)
	{
		for (var Index = 0; Index < this.Content.length; Index++)
		{
			var Item = this.Content[Index];
			Item.Set_ApplyToAll(true);
			Item.SetParagraphTabs(Tabs);
			Item.Set_ApplyToAll(false);
		}

		return;
	}

	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.setParagraphTabs(Tabs);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (this.CurPos.ContentPos < 0)
			return false;

		if (true === this.Selection.Use)
		{
			var StartPos = this.Selection.StartPos;
			var EndPos   = this.Selection.EndPos;
			if (EndPos < StartPos)
			{
				var Temp = StartPos;
				StartPos = EndPos;
				EndPos   = Temp;
			}

			for (var Index = StartPos; Index <= EndPos; Index++)
			{
				var Item = this.Content[Index];
				Item.SetParagraphTabs(Tabs);
			}
		}
		else
		{
			var Item = this.Content[this.CurPos.ContentPos];
			Item.SetParagraphTabs(Tabs);
		}
	}
};
CDocumentContent.prototype.SetParagraphContextualSpacing = function(Value)
{
	if (true === this.ApplyToAll)
	{
		for (var Index = 0; Index < this.Content.length; Index++)
		{
			var Item = this.Content[Index];
			Item.Set_ApplyToAll(true);
			Item.SetParagraphContextualSpacing(Value);
			Item.Set_ApplyToAll(false);
		}

		return;
	}

	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.setParagraphContextualSpacing(Value);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (this.CurPos.ContentPos < 0)
			return false;

		if (true === this.Selection.Use)
		{
			var StartPos = this.Selection.StartPos;
			var EndPos   = this.Selection.EndPos;
			if (EndPos < StartPos)
			{
				var Temp = StartPos;
				StartPos = EndPos;
				EndPos   = Temp;
			}

			for (var Index = StartPos; Index <= EndPos; Index++)
			{
				var Item = this.Content[Index];
				Item.SetParagraphContextualSpacing(Value);
			}
		}
		else
		{
			var Item = this.Content[this.CurPos.ContentPos];
			Item.SetParagraphContextualSpacing(Value);
		}
	}
};
CDocumentContent.prototype.SetParagraphPageBreakBefore = function(Value)
{
	// Ничего не делаем
};
CDocumentContent.prototype.SetParagraphKeepLines = function(Value)
{
	if (true === this.ApplyToAll)
	{
		for (var Index = 0; Index < this.Content.length; Index++)
		{
			var Item = this.Content[Index];
			Item.Set_ApplyToAll(true);
			Item.SetParagraphKeepLines(Value);
			Item.Set_ApplyToAll(false);
		}

		return;
	}

	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.setParagraphKeepLines(Value);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (this.CurPos.ContentPos < 0)
			return false;

		if (true === this.Selection.Use)
		{
			var StartPos = this.Selection.StartPos;
			var EndPos   = this.Selection.EndPos;
			if (EndPos < StartPos)
			{
				var Temp = StartPos;
				StartPos = EndPos;
				EndPos   = Temp;
			}

			for (var Index = StartPos; Index <= EndPos; Index++)
			{
				var Item = this.Content[Index];
				Item.SetParagraphKeepLines(Value);
			}
		}
		else
		{
			var Item = this.Content[this.CurPos.ContentPos];
			Item.SetParagraphKeepLines(Value);
		}
	}
};
CDocumentContent.prototype.SetParagraphKeepNext = function(Value)
{
	if (true === this.ApplyToAll)
	{
		for (var Index = 0; Index < this.Content.length; Index++)
		{
			var Item = this.Content[Index];
			Item.Set_ApplyToAll(true);
			Item.SetParagraphKeepNext(Value);
			Item.Set_ApplyToAll(false);
		}

		return;
	}

	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.setParagraphKeepNext(Value);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (this.CurPos.ContentPos < 0)
			return false;

		if (true === this.Selection.Use)
		{
			var StartPos = this.Selection.StartPos;
			var EndPos   = this.Selection.EndPos;
			if (EndPos < StartPos)
			{
				var Temp = StartPos;
				StartPos = EndPos;
				EndPos   = Temp;
			}

			for (var Index = StartPos; Index <= EndPos; Index++)
			{
				var Item = this.Content[Index];
				Item.SetParagraphKeepNext(Value);
			}
		}
		else
		{
			var Item = this.Content[this.CurPos.ContentPos];
			Item.SetParagraphKeepNext(Value);
		}
	}
};
CDocumentContent.prototype.SetParagraphWidowControl = function(Value)
{
	if (true === this.ApplyToAll)
	{
		for (var Index = 0; Index < this.Content.length; Index++)
		{
			var Item = this.Content[Index];
			Item.Set_ApplyToAll(true);
			Item.SetParagraphWidowControl(Value);
			Item.Set_ApplyToAll(false);
		}

		return;
	}

	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.setParagraphWidowControl(Value);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (this.CurPos.ContentPos < 0)
			return false;

		if (true === this.Selection.Use)
		{
			var StartPos = this.Selection.StartPos;
			var EndPos   = this.Selection.EndPos;
			if (EndPos < StartPos)
			{
				var Temp = StartPos;
				StartPos = EndPos;
				EndPos   = Temp;
			}

			for (var Index = StartPos; Index <= EndPos; Index++)
			{
				var Item = this.Content[Index];
				Item.SetParagraphWidowControl(Value);
			}
		}
		else
		{
			var Item = this.Content[this.CurPos.ContentPos];
			Item.SetParagraphWidowControl(Value);
		}
	}
};
CDocumentContent.prototype.SetParagraphBorders = function(Borders)
{
	if (true === this.ApplyToAll)
	{
		for (var Index = 0; Index < this.Content.length; Index++)
		{
			var Item = this.Content[Index];
			Item.Set_ApplyToAll(true);
			Item.SetParagraphBorders(Borders);
			Item.Set_ApplyToAll(false);
		}

		return;
	}

	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.setParagraphBorders(Borders);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (this.CurPos.ContentPos < 0)
			return false;

		if (true === this.Selection.Use)
		{
			var StartPos = this.Selection.StartPos;
			var EndPos   = this.Selection.EndPos;
			if (EndPos < StartPos)
			{
				var Temp = StartPos;
				StartPos = EndPos;
				EndPos   = Temp;
			}

			for (var Index = StartPos; Index <= EndPos; Index++)
			{
				var Item = this.Content[Index];
				Item.SetParagraphBorders(Borders);
			}
		}
		else
		{
			var Item = this.Content[this.CurPos.ContentPos];
			if (type_Paragraph === Item.GetType())
			{
				// Мы должны выставить границу для всех параграфов, входящих в текущую группу параграфов
				// с одинаковыми границами

				var StartPos = Item.Index;
				var EndPos   = Item.Index;
				var CurBrd   = Item.Get_CompiledPr().ParaPr.Brd;

				while (true != CurBrd.First)
				{
					StartPos--;
					if (StartPos < 0)
					{
						StartPos = 0;
						break;
					}

					var TempItem = this.Content[StartPos];
					if (type_Paragraph !== TempItem.GetType())
					{
						StartPos++;
						break;
					}

					CurBrd = TempItem.Get_CompiledPr().ParaPr.Brd;
				}

				CurBrd = Item.Get_CompiledPr().ParaPr.Brd;
				while (true != CurBrd.Last)
				{
					EndPos++;
					if (EndPos >= this.Content.length)
					{
						EndPos = this.Content.length - 1;
						break;
					}

					var TempItem = this.Content[EndPos];
					if (type_Paragraph !== TempItem.GetType())
					{
						EndPos--;
						break;
					}

					CurBrd = TempItem.Get_CompiledPr().ParaPr.Brd;
				}

				for (var Index = StartPos; Index <= EndPos; Index++)
					this.Content[Index].SetParagraphBorders(Borders);
			}
			else
			{
				Item.SetParagraphBorders(Borders);
			}
		}
	}
};
CDocumentContent.prototype.IncreaseDecreaseFontSize = function(bIncrease)
{
	if (true === this.ApplyToAll)
	{
		for (var Index = 0; Index < this.Content.length; Index++)
		{
			var Item = this.Content[Index];
			Item.Set_ApplyToAll(true);
			Item.IncreaseDecreaseFontSize(bIncrease);
			Item.Set_ApplyToAll(false);
		}

		return;
	}

	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.paragraphIncDecFontSize(bIncrease);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (this.CurPos.ContentPos < 0)
			return false;

		if (true === this.Selection.Use)
		{
			switch (this.Selection.Flag)
			{
				case selectionflag_Common:
				{
					var StartPos = this.Selection.StartPos;
					var EndPos   = this.Selection.EndPos;
					if (EndPos < StartPos)
					{
						var Temp = StartPos;
						StartPos = EndPos;
						EndPos   = Temp;
					}

					for (var Index = StartPos; Index <= EndPos; Index++)
					{
						var Item = this.Content[Index];
						Item.IncreaseDecreaseFontSize(bIncrease);
					}
					break;
				}
				case  selectionflag_Numbering:
				{
					var OldFontSize = this.GetCalculatedTextPr().FontSize;
					var NewFontSize = FontSize_IncreaseDecreaseValue(bIncrease, OldFontSize);
					var TextPr      = new CTextPr();
					TextPr.FontSize = NewFontSize;
					this.AddToParagraph(new ParaTextPr(TextPr), true);
					break;
				}
			}
		}
		else
		{
			var Item = this.Content[this.CurPos.ContentPos];
			Item.IncreaseDecreaseFontSize(bIncrease);
		}
	}
};
CDocumentContent.prototype.IncreaseDecreaseIndent = function(bIncrease)
{
	if (true === this.ApplyToAll)
	{
		for (var Index = 0; Index < this.Content.length; Index++)
		{
			var Item = this.Content[Index];
			Item.Set_ApplyToAll(true);
			Item.IncreaseDecreaseIndent(bIncrease);
			Item.Set_ApplyToAll(false);
		}

		return;
	}

	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		if (true != this.LogicDocument.DrawingObjects.isSelectedText())
		{
			var ParaDrawing = this.LogicDocument.DrawingObjects.getMajorParaDrawing();
			if (null != ParaDrawing)
			{
				var Paragraph = ParaDrawing.Parent;
				Paragraph.IncreaseDecreaseIndent(bIncrease);
			}
		}
		else
		{
			this.DrawingObjects.paragraphIncDecIndent(bIncrease);
		}
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (true === this.Selection.Use && selectionflag_Common === this.Selection.Flag)
		{
			var StartPos = this.Selection.StartPos;
			var EndPos   = this.Selection.EndPos;
			if (EndPos < StartPos)
			{
				var Temp = StartPos;
				StartPos = EndPos;
				EndPos   = Temp;
			}

			for (var Index = StartPos; Index <= EndPos; Index++)
			{
				this.Content[Index].IncreaseDecreaseIndent(bIncrease);
			}
		}
		else
		{
			this.Content[this.CurPos.ContentPos].IncreaseDecreaseIndent(bIncrease);
		}
	}
};
CDocumentContent.prototype.PasteFormatting = function(TextPr, ParaPr, ApplyPara)
{
	if (true === this.ApplyToAll)
	{
		for (var Index = 0; Index < this.Content.length; Index++)
		{
			var Item = this.Content[Index];
			Item.Set_ApplyToAll(true);
			Item.PasteFormatting(TextPr, ParaPr, true);
			Item.Set_ApplyToAll(false);
		}

		return;
	}

	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.paragraphFormatPaste(TextPr, ParaPr, ApplyPara);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (true === this.Selection.Use)
		{
			switch (this.Selection.Flag)
			{
				case selectionflag_Numbering    :
					return;
				case selectionflag_Common:
				{
					var Start = this.Selection.StartPos;
					var End   = this.Selection.EndPos;
					if (Start > End)
					{
						Start = this.Selection.EndPos;
						End   = this.Selection.StartPos;
					}

					for (var Pos = Start; Pos <= End; Pos++)
					{
						this.Content[Pos].PasteFormatting(TextPr, ParaPr, ( Start === End ? false : true ));
					}
					break;
				}
			}
		}
		else
		{
			this.Content[this.CurPos.ContentPos].PasteFormatting(TextPr, ParaPr, true);
		}
	}
};
CDocumentContent.prototype.SetImageProps = function(Props)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		this.LogicDocument.DrawingObjects.setProps(Props);
		this.Document_UpdateInterfaceState();
	}
	else if (docpostype_Content == this.CurPos.Type && ( ( true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Table == this.Content[this.Selection.StartPos].GetType() ) || ( false == this.Selection.Use && type_Table == this.Content[this.CurPos.ContentPos].GetType() ) ))
	{
		if (true == this.Selection.Use)
			this.Content[this.Selection.StartPos].SetImageProps(Props);
		else
			this.Content[this.CurPos.ContentPos].SetImageProps(Props);
	}
};
CDocumentContent.prototype.SetTableProps = function(Props)
{
	if (true === this.ApplyToAll)
		return false;

	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.setTableProps(Props);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		var Pos = -1;
		if (true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos)
			Pos = this.Selection.StartPos;
		else if (false === this.Selection.Use)
			Pos = this.CurPos.ContentPos;

		if (-1 !== Pos)
			return this.Content[Pos].SetTableProps(Props);

		return false;
	}
};
CDocumentContent.prototype.GetTableProps = function()
{
	var TablePr = null;
	if (docpostype_Content == this.Get_DocPosType() && ((true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos) || false == this.Selection.Use))
	{
		if (true == this.Selection.Use)
			TablePr = this.Content[this.Selection.StartPos].GetTableProps();
		else
			TablePr = this.Content[this.CurPos.ContentPos].GetTableProps();
	}

	if (null !== TablePr)
		TablePr.CanBeFlow = true;

	return TablePr;
};
CDocumentContent.prototype.GetCalculatedParaPr = function()
{
	var Result_ParaPr = new CParaPr();

	if (true === this.ApplyToAll)
	{
		var StartPr = this.Content[0].GetCalculatedParaPr();
		var Pr      = StartPr.Copy();
		Pr.Locked   = StartPr.Locked;

		for (var Index = 1; Index < this.Content.length; Index++)
		{
			var TempPr = this.Content[Index].GetCalculatedParaPr();
			Pr         = Pr.Compare(TempPr);
		}

		if (Pr.Ind.Left == UnknownValue)
			Pr.Ind.Left = StartPr.Ind.Left;

		if (Pr.Ind.Right == UnknownValue)
			Pr.Ind.Right = StartPr.Ind.Right;

		if (Pr.Ind.FirstLine == UnknownValue)
			Pr.Ind.FirstLine = StartPr.Ind.FirstLine;

		Result_ParaPr             = Pr;
		Result_ParaPr.CanAddTable = ( true === Pr.Locked ? false : true ) && !(this.bPresentation === true);
		if (Result_ParaPr.Shd && Result_ParaPr.Shd.Unifill)
		{
			Result_ParaPr.Shd.Unifill.check(this.Get_Theme(), this.Get_ColorMap());
		}
		return Result_ParaPr;
	}

	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.getParagraphParaPr();
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (true === this.Selection.Use && selectionflag_Common === this.Selection.Flag)
		{
			var StartPos = this.Selection.StartPos;
			var EndPos   = this.Selection.EndPos;
			if (EndPos < StartPos)
			{
				var Temp = StartPos;
				StartPos = EndPos;
				EndPos   = Temp;
			}

			var StartPr = this.Content[StartPos].GetCalculatedParaPr();
			var Pr      = StartPr.Copy();
			Pr.Locked   = StartPr.Locked;

			for (var Index = StartPos + 1; Index <= EndPos; Index++)
			{
				var TempPr = this.Content[Index].GetCalculatedParaPr();
				Pr         = Pr.Compare(TempPr);
			}

			if (undefined === Pr.Ind.Left)
				Pr.Ind.Left = StartPr.Ind.Left;

			if (undefined === Pr.Ind.Right)
				Pr.Ind.Right = StartPr.Ind.Right;

			if (undefined === Pr.Ind.FirstLine)
				Pr.Ind.FirstLine = StartPr.Ind.FirstLine;

			Result_ParaPr             = Pr;
			Result_ParaPr.CanAddTable = ( true === Pr.Locked ? false : true ) && !(this.bPresentation === true);
		}
		else
		{
			var Item = this.Content[this.CurPos.ContentPos];
			if (type_Paragraph == Item.GetType())
			{
				var ParaPr = Item.Get_CompiledPr2(false).ParaPr;
				var Locked = Item.Lock.Is_Locked();

				Result_ParaPr             = ParaPr.Copy();
				Result_ParaPr.Locked      = Locked;
				Result_ParaPr.CanAddTable = ( ( true === Locked ) ? ( ( true === Item.IsCursorAtEnd() ) ? true : false ) : true ) && !(this.bPresentation === true);
			}
			else
			{
				Result_ParaPr = Item.GetCalculatedParaPr();
			}
		}

		if (Result_ParaPr.Shd && Result_ParaPr.Shd.Unifill)
		{
			Result_ParaPr.Shd.Unifill.check(this.Get_Theme(), this.Get_ColorMap());
		}
		return Result_ParaPr;
	}
};
CDocumentContent.prototype.GetCalculatedTextPr = function()
{
	var Result_TextPr = null;

	if (true === this.ApplyToAll)
	{
		var VisTextPr;
		this.Content[0].Set_ApplyToAll(true);
		VisTextPr = this.Content[0].GetCalculatedTextPr();
		this.Content[0].Set_ApplyToAll(false);

		var Count = this.Content.length;
		for (var Index = 1; Index < Count; Index++)
		{
			this.Content[Index].Set_ApplyToAll(true);
			var CurPr = this.Content[Index].GetCalculatedTextPr();
			VisTextPr = VisTextPr.Compare(CurPr);
			this.Content[Index].Set_ApplyToAll(false);
		}

		Result_TextPr = VisTextPr;

		return Result_TextPr;
	}

	if (docpostype_DrawingObjects === this.CurPos.Type)
		return this.LogicDocument.DrawingObjects.getParagraphTextPr();
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (true === this.Selection.Use)
		{
			var VisTextPr;
			switch (this.Selection.Flag)
			{
				case selectionflag_Common:
				{
					var StartPos = this.Selection.StartPos;
					var EndPos   = this.Selection.EndPos;
					if (EndPos < StartPos)
					{
						var Temp = StartPos;
						StartPos = EndPos;
						EndPos   = Temp;
					}

					VisTextPr = this.Content[StartPos].GetCalculatedTextPr();

					for (var Index = StartPos + 1; Index <= EndPos; Index++)
					{
						var CurPr = this.Content[Index].GetCalculatedTextPr();
						VisTextPr = VisTextPr.Compare(CurPr);
					}

					break;
				}
				case selectionflag_Numbering:
				{
					// Текстовые настройки применяем к конкретной нумерации
					if (null == this.Selection.Data || this.Selection.Data.length <= 0)
						break;

					var CurPara = this.Content[this.Selection.Data[0]];
					for (var Index = 0; Index < this.Selection.Data.length; Index++)
					{
						if (this.CurPos.ContentPos === this.Selection.Data[Index])
							CurPara = this.Content[this.Selection.Data[Index]];
					}

					VisTextPr = CurPara.Internal_Get_NumberingTextPr();

					break;
				}
			}

			Result_TextPr = VisTextPr;
		}
		else
		{
			Result_TextPr = this.Content[this.CurPos.ContentPos].GetCalculatedTextPr();
		}

		return Result_TextPr;
	}
};
CDocumentContent.prototype.GetDirectTextPr = function()
{
	var Result_TextPr = null;

	if (true === this.ApplyToAll)
	{
		var Item      = this.Content[0];
		Result_TextPr = Item.GetDirectTextPr();
		return Result_TextPr;
	}

	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.getParagraphTextPrCopy();
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (true === this.Selection.Use)
		{
			var VisTextPr;
			switch (this.Selection.Flag)
			{
				case selectionflag_Common:
				{
					var StartPos = this.Selection.StartPos;
					if (this.Selection.EndPos < StartPos)
						StartPos = this.Selection.EndPos;

					var Item  = this.Content[StartPos];
					VisTextPr = Item.GetDirectTextPr();

					break;
				}
				case selectionflag_Numbering:
				{
					// Текстовые настройки применяем к конкретной нумерации
					if (null == this.Selection.Data || this.Selection.Data.length <= 0)
						break;

					var NumPr = this.Content[this.Selection.Data[0]].Numbering_Get();
					VisTextPr = this.Numbering.Get_AbstractNum(NumPr.NumId).Lvl[NumPr.Lvl].TextPr;

					break;
				}
			}

			Result_TextPr = VisTextPr;
		}
		else
		{
			var Item      = this.Content[this.CurPos.ContentPos];
			Result_TextPr = Item.GetDirectTextPr();
		}

		return Result_TextPr;
	}
};
CDocumentContent.prototype.GetDirectParaPr = function()
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.getParagraphParaPrCopy();
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		var Result_ParaPr = null;

		// Inline объекты
		if (docpostype_Content == this.CurPos.Type)
		{
			if (true === this.Selection.Use)
			{
				switch (this.Selection.Flag)
				{
					case selectionflag_Common:
					{
						var StartPos = this.Selection.StartPos;
						if (this.Selection.EndPos < StartPos)
							StartPos = this.Selection.EndPos;

						var Item      = this.Content[StartPos];
						Result_ParaPr = Item.GetDirectParaPr();

						break;
					}
					case selectionflag_Numbering:
					{
						// Текстовые настройки применяем к конкретной нумерации
						if (null == this.Selection.Data || this.Selection.Data.length <= 0)
							break;

						var NumPr     = this.Content[this.Selection.Data[0]].Numbering_Get();
						Result_ParaPr = this.Numbering.Get_AbstractNum(NumPr.NumId).Lvl[NumPr.Lvl].ParaPr;

						break;
					}
				}
			}
			else
			{
				var Item      = this.Content[this.CurPos.ContentPos];
				Result_ParaPr = Item.GetDirectParaPr();
			}
		}

		return Result_ParaPr;
	}
};
//-----------------------------------------------------------------------------------
// Функции для работы с интерфейсом
//-----------------------------------------------------------------------------------

// Обновляем данные в интерфейсе о свойствах параграфа
CDocumentContent.prototype.Interface_Update_ParaPr    = function()
{
    var ParaPr = this.GetCalculatedParaPr();

    if (null != ParaPr)
    {
        ParaPr.CanAddDropCap = false;

        if (this.LogicDocument)
        {
            var oSelectedInfo = this.LogicDocument.GetSelectedElementsInfo();
            var Math          = oSelectedInfo.Get_Math();
            if (null !== Math)
                ParaPr.CanAddImage = false;
            else
                ParaPr.CanAddImage = true;
        }

        if (undefined != ParaPr.Tabs && editor)
            editor.Update_ParaTab(AscCommonWord.Default_Tab_Stop, ParaPr.Tabs);

        if (this.LogicDocument)
        {
            var SelectedInfo = this.LogicDocument.GetSelectedElementsInfo();
            var Math         = SelectedInfo.Get_Math();
            if (null !== Math && true !== Math.Is_Inline())
                ParaPr.Jc = Math.Get_Align();

            // Если мы находимся внутри автофигуры, тогда нам надо проверить лок параграфа, в котором находится автофигура
            if (docpostype_DrawingObjects === this.LogicDocument.CurPos.Type && true !== ParaPr.Locked)
            {
                var ParaDrawing = this.LogicDocument.DrawingObjects.getMajorParaDrawing();
                if (ParaDrawing)
                {
                    ParaPr.Locked = ParaDrawing.Lock.Is_Locked();
                }
            }
        }

        if (editor)
            editor.UpdateParagraphProp(ParaPr);
    }
};
// Обновляем данные в интерфейсе о свойствах текста
CDocumentContent.prototype.Interface_Update_TextPr    = function()
{
    var TextPr = this.GetCalculatedTextPr();


    if (null != TextPr)
    {
        var theme = this.Get_Theme();
        if (theme && theme.themeElements && theme.themeElements.fontScheme)
        {
            if (TextPr.FontFamily)
            {
                TextPr.FontFamily.Name = theme.themeElements.fontScheme.checkFont(TextPr.FontFamily.Name);
            }
            if (TextPr.RFonts)
            {
                if (TextPr.RFonts.Ascii)
                    TextPr.RFonts.Ascii.Name = theme.themeElements.fontScheme.checkFont(TextPr.RFonts.Ascii.Name);
                if (TextPr.RFonts.EastAsia)
                    TextPr.RFonts.EastAsia.Name = theme.themeElements.fontScheme.checkFont(TextPr.RFonts.EastAsia.Name);
                if (TextPr.RFonts.HAnsi)
                    TextPr.RFonts.HAnsi.Name = theme.themeElements.fontScheme.checkFont(TextPr.RFonts.HAnsi.Name);
                if (TextPr.RFonts.CS)
                    TextPr.RFonts.CS.Name = theme.themeElements.fontScheme.checkFont(TextPr.RFonts.CS.Name);
            }
        }
        editor.UpdateTextPr(TextPr);
    }
};
CDocumentContent.prototype.Interface_Update_DrawingPr = function(Flag)
{
    var ImagePr = {};

    if (docpostype_DrawingObjects === this.CurPos.Type)
        ImagePr = this.LogicDocument.DrawingObjects.getProps();

    if (true === Flag)
        return ImagePr;
    else
        editor.sync_ImgPropCallback(ImagePr);

};
CDocumentContent.prototype.Interface_Update_TablePr   = function(Flag)
{
    var TablePr = null;
    if (docpostype_DrawingObjects == this.CurPos.Type)
    {
        TablePr = this.LogicDocument.DrawingObjects.getTableProps();
    }
    else if (docpostype_Content == this.CurPos.Type && ( ( true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Table == this.Content[this.Selection.StartPos].GetType() ) || ( false == this.Selection.Use && type_Table == this.Content[this.CurPos.ContentPos].GetType() ) ))
    {
        if (true == this.Selection.Use)
            TablePr = this.Content[this.Selection.StartPos].Get_Props();
        else
            TablePr = this.Content[this.CurPos.ContentPos].Get_Props();
    }

    if (true === Flag)
        return TablePr;
    else if (null != TablePr)
        editor.sync_TblPropCallback(TablePr);
};
//-----------------------------------------------------------------------------------
// Функции для работы с селектом
//-----------------------------------------------------------------------------------
CDocumentContent.prototype.RemoveSelection = function(bNoCheckDrawing)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.resetSelection(undefined, bNoCheckDrawing);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (true === this.Selection.Use)
		{
			switch (this.Selection.Flag)
			{
				case selectionflag_Common:
				{
					var Start = this.Selection.StartPos;
					var End   = this.Selection.EndPos;

					if (Start > End)
					{
						var Temp = Start;
						Start    = End;
						End      = Temp;
					}

					Start = Math.max(0, Start);
					End   = Math.min(this.Content.length - 1, End);

					for (var Index = Start; Index <= End; Index++)
					{
						this.Content[Index].RemoveSelection();
					}
					break;
				}
				case selectionflag_Numbering:
				{
					if (null == this.Selection.Data)
						break;

					for (var Index = 0; Index < this.Selection.Data.length; Index++)
					{
						this.Content[this.Selection.Data[Index]].RemoveSelection();
					}
					break;
				}
			}
		}

		this.Selection.StartPos = 0;
		this.Selection.EndPos   = 0;

		this.Selection.Use   = false;
		this.Selection.Start = false;
		this.Selection.Flag  = selectionflag_Common;
	}
};
CDocumentContent.prototype.DrawSelectionOnPage = function(PageIndex)
{
    var CurPage = PageIndex;
    if (CurPage < 0 || CurPage >= this.Pages.length)
        return;

    if (docpostype_DrawingObjects === this.CurPos.Type)
    {
        this.DrawingDocument.SetTextSelectionOutline(true);
        var PageAbs = CurPage + this.Get_StartPage_Absolute();
        this.LogicDocument.DrawingObjects.drawSelectionPage(PageAbs);
    }
    else
    {
        var Pos_start = this.Pages[CurPage].Pos;
        var Pos_end   = this.Pages[CurPage].EndPos;

        if (true === this.Selection.Use)
        {
            switch (this.Selection.Flag)
            {
                case selectionflag_Common:
                {
                    var Start = this.Selection.StartPos;
                    var End   = this.Selection.EndPos;

                    if (Start > End)
                    {
                        Start = this.Selection.EndPos;
                        End   = this.Selection.StartPos;
                    }

                    var Start = Math.max(Start, Pos_start);
                    var End   = Math.min(End, Pos_end);

                    for (var Index = Start; Index <= End; Index++)
                    {
                        var ElementPageIndex = this.private_GetElementPageIndex(Index, CurPage, 0, 1);
                        this.Content[Index].DrawSelectionOnPage(ElementPageIndex);
                    }

                    break;
                }
                case selectionflag_Numbering:
                {
                    if (null == this.Selection.Data)
                        break;

                    var Count = this.Selection.Data.length;

                    for (var Index = 0; Index < Count; Index++)
                    {
                        if (this.Selection.Data[Index] <= Pos_end && this.Selection.Data[Index] >= Pos_start)
                        {
                            var ElementPageIndex = this.private_GetElementPageIndex(this.Selection.Data[Index], CurPage, 0, 1);
                            this.Content[this.Selection.Data[Index]].DrawSelectionOnPage(ElementPageIndex);
                        }
                    }

                    break;
                }
            }
        }
    }
};
CDocumentContent.prototype.Selection_SetStart = function(X, Y, CurPage, MouseEvent)
{
	if (this.Pages.length <= 0)
		return;

	if (CurPage < 0)
	{
		CurPage = 0;
		Y       = 0;
	}
	else if (CurPage >= this.Pages.length)
	{
		CurPage = this.Pages.length - 1;
		Y       = this.Pages[CurPage].YLimit;
	}

	this.CurPage = CurPage;
	var AbsPage  = this.Get_AbsolutePage(this.CurPage);

	// Сначала проверим, не попали ли мы в один из "плавающих" объектов
	var bInText      = (null === this.IsInText(X, Y, AbsPage) ? false : true);
	var bTableBorder = (null === this.IsTableBorder(X, Y, AbsPage) ? false : true);
	var nInDrawing   = this.LogicDocument && this.LogicDocument.DrawingObjects.IsInDrawingObject(X, Y, AbsPage, this);

	if (this.Parent instanceof CHeaderFooter && ( nInDrawing === DRAWING_ARRAY_TYPE_BEFORE || nInDrawing === DRAWING_ARRAY_TYPE_INLINE || ( false === bTableBorder && false === bInText && nInDrawing >= 0 ) ))
	{
		if (docpostype_DrawingObjects != this.CurPos.Type)
			this.RemoveSelection();

		// Прячем курсор
		this.DrawingDocument.TargetEnd();
		this.DrawingDocument.SetCurrentPage(AbsPage);

		var HdrFtr = this.Is_HdrFtr(true);
		if (null === HdrFtr)
		{
			this.LogicDocument.Selection.Use   = true;
			this.LogicDocument.Selection.Start = true;
			this.LogicDocument.Selection.Flag  = selectionflag_Common;
			this.LogicDocument.Set_DocPosType(docpostype_DrawingObjects);
		}
		else
		{
			HdrFtr.Content.Selection.Use   = true;
			HdrFtr.Content.Selection.Start = true;
			HdrFtr.Content.Selection.Flag  = selectionflag_Common;
			HdrFtr.Content.Set_DocPosType(docpostype_DrawingObjects);
		}

		this.LogicDocument.DrawingObjects.OnMouseDown(MouseEvent, X, Y, AbsPage);
	}
	else
	{
		var bOldSelectionIsCommon = true;

		if (docpostype_DrawingObjects === this.CurPos.Type && true != this.IsInDrawing(X, Y, AbsPage))
		{
			this.LogicDocument.DrawingObjects.resetSelection();
			bOldSelectionIsCommon = false;
		}

		var ContentPos = this.Internal_GetContentPosByXY(X, Y);

		if (docpostype_Content != this.CurPos.Type)
		{
			this.Set_DocPosType(docpostype_Content);
			this.CurPos.ContentPos = ContentPos;
			bOldSelectionIsCommon  = false;
		}

		var SelectionUse_old = this.Selection.Use;
		var Item             = this.Content[ContentPos];
		var bTableBorder     = (null != Item.IsTableBorder(X, Y, AbsPage) ? true : false);

		// Убираем селект, кроме случаев либо текущего параграфа, либо при движении границ внутри таблицы
		if (!(true === SelectionUse_old && true === MouseEvent.ShiftKey && true === bOldSelectionIsCommon))
		{
			if ((selectionflag_Common != this.Selection.Flag) || ( true === this.Selection.Use && MouseEvent.ClickCount <= 1 && true != bTableBorder ))
				this.RemoveSelection();
		}

		this.Selection.Use   = true;
		this.Selection.Start = true;
		this.Selection.Flag  = selectionflag_Common;

		if (true === SelectionUse_old && true === MouseEvent.ShiftKey && true === bOldSelectionIsCommon)
		{
			this.Selection_SetEnd(X, Y, this.CurPage, {Type : AscCommon.g_mouse_event_type_up, ClickCount : 1});
			this.Selection.Use    = true;
			this.Selection.Start  = true;
			this.Selection.EndPos = ContentPos;
			this.Selection.Data   = null;
		}
		else
		{
			var ElementPageIndex = this.private_GetElementPageIndexByXY(ContentPos, X, Y, this.CurPage);
			Item.Selection_SetStart(X, Y, ElementPageIndex, MouseEvent);
			Item.Selection_SetEnd(X, Y, ElementPageIndex, {Type : AscCommon.g_mouse_event_type_move, ClickCount : 1});

			if (true !== bTableBorder)
			{
				this.Selection.Use      = true;
				this.Selection.StartPos = ContentPos;
				this.Selection.EndPos   = ContentPos;
				this.Selection.Data     = null;

				this.CurPos.ContentPos = ContentPos;

				if (type_Paragraph === Item.GetType() && true === MouseEvent.CtrlKey)
				{
					var oHyperlink   = Item.CheckHyperlink(X, Y, ElementPageIndex);
					var oPageRefLink = Item.CheckPageRefLink(X, Y, ElementPageIndex);
					if (null != oHyperlink)
					{
						this.Selection.Data = {
							Hyperlink : oHyperlink
						};
					}
					else if (null !== oPageRefLink)
					{
						this.Selection.Data = {
							PageRef : oPageRefLink
						};
					}
				}
			}
			else
			{
				this.Selection.Data = {
					TableBorder : true,
					Pos         : ContentPos,
					Selection   : SelectionUse_old
				};
			}
		}
	}
};
// Данная функция может использоваться как при движении, так и при окончательном выставлении селекта.
// Если bEnd = true, тогда это конец селекта.
CDocumentContent.prototype.Selection_SetEnd = function(X, Y, CurPage, MouseEvent)
{
	if (this.Pages.length <= 0)
		return;

	if (CurPage < 0)
	{
		CurPage = 0;
		Y       = 0;
	}
	else if (CurPage >= this.Pages.length)
	{
		CurPage = this.Pages.length - 1;
		Y       = this.Pages[CurPage].YLimit;
	}

	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		var PageAbs = this.Get_StartPage_Absolute(CurPage);
		if (AscCommon.g_mouse_event_type_up == MouseEvent.Type)
		{
			this.LogicDocument.DrawingObjects.OnMouseUp(MouseEvent, X, Y, PageAbs);
			this.Selection.Start = false;
			this.Selection.Use   = true;
		}
		else
		{
			this.LogicDocument.DrawingObjects.OnMouseMove(MouseEvent, X, Y, PageAbs);
		}
		return;
	}

	this.CurPage = CurPage;

	if (selectionflag_Numbering === this.Selection.Flag)
		return;

	// Обрабатываем движение границы у таблиц
	if (null != this.Selection.Data && true === this.Selection.Data.TableBorder && type_Table == this.Content[this.Selection.Data.Pos].GetType())
	{
		var Item             = this.Content[this.Selection.Data.Pos];
		var ElementPageIndex = this.private_GetElementPageIndexByXY(this.Selection.Data.Pos, X, Y, this.CurPage);
		Item.Selection_SetEnd(X, Y, ElementPageIndex, MouseEvent);

		if (AscCommon.g_mouse_event_type_up == MouseEvent.Type)
		{
			this.Selection.Start = false;

			if (true != this.Selection.Data.Selection)
			{
				this.Selection.Use = false;
			}
			this.Selection.Data = null;
		}

		return;
	}

	if (false === this.Selection.Use)
		return;

	var ContentPos = this.Internal_GetContentPosByXY(X, Y);

	var OldPos      = this.CurPos.ContentPos;
	var OldInnerPos = null;
	if (type_Paragraph === this.Content[OldPos].GetType())
		OldInnerPos = this.Content[OldPos].CurPos.ContentPos;
	else //if ( type_Table === this.Content[OldPos].GetType() )
		OldInnerPos = this.Content[OldPos].CurCell;

	this.CurPos.ContentPos = ContentPos;
	var OldEndPos          = this.Selection.EndPos;
	this.Selection.EndPos  = ContentPos;

	// Удалим отметки о старом селекте
	if (OldEndPos < this.Selection.StartPos && OldEndPos < this.Selection.EndPos)
	{
		var TempLimit = Math.min(this.Selection.StartPos, this.Selection.EndPos);
		for (var Index = OldEndPos; Index < TempLimit; Index++)
		{
			this.Content[Index].RemoveSelection();
		}
	}
	else if (OldEndPos > this.Selection.StartPos && OldEndPos > this.Selection.EndPos)
	{
		var TempLimit = Math.max(this.Selection.StartPos, this.Selection.EndPos);
		for (var Index = TempLimit + 1; Index <= OldEndPos; Index++)
		{
			this.Content[Index].RemoveSelection();
		}
	}

	// Направление селекта: 1 - прямое, -1 - обратное, 0 - отмечен 1 элемент документа
	var Direction = ( ContentPos > this.Selection.StartPos ? 1 : ( ContentPos < this.Selection.StartPos ? -1 : 0 )  );

	if (AscCommon.g_mouse_event_type_up == MouseEvent.Type)
		this.StopSelection();

	var Start, End;
	if (0 == Direction)
	{
		var Item             = this.Content[this.Selection.StartPos];
		var ElementPageIndex = this.private_GetElementPageIndexByXY(this.Selection.StartPos, X, Y, this.CurPage);
		Item.Selection_SetEnd(X, Y, ElementPageIndex, MouseEvent);

		if (false === Item.IsSelectionUse())
		{
			this.Selection.Use = false;

			if (null != this.Selection.Data && this.Selection.Data.Hyperlink)
			{
				editor && editor.sync_HyperlinkClickCallback(this.Selection.Data.Hyperlink.Get_Value());
				this.Selection.Data.Hyperlink.Set_Visited(true);

				if (this.DrawingDocument.m_oLogicDocument)
				{
					if (editor.isDocumentEditor)
					{
						for (var PageIdx = Item.Get_StartPage_Absolute(); PageIdx < Item.Get_StartPage_Absolute() + Item.Pages.length; PageIdx++)
							this.DrawingDocument.OnRecalculatePage(PageIdx, this.DrawingDocument.m_oLogicDocument.Pages[PageIdx]);
					}
					else
					{
						this.DrawingDocument.OnRecalculatePage(PageIdx, this.DrawingDocument.m_oLogicDocument.Slides[PageIdx]);
					}
					this.DrawingDocument.OnEndRecalculate(false, true);
				}
			}
			else if (null !== this.Selection.Data && this.Selection.Data.PageRef)
			{
				var oInstruction  = this.Selection.Data.PageRef.GetInstruction();
				if (oInstruction && fieldtype_PAGEREF === oInstruction.GetType())
				{
					var oBookmark = this.BookmarksManager.GetBookmarkByName(oInstruction.GetBookmarkName());
					if (oBookmark)
						oBookmark[0].GoToBookmark();
				}
			}
		}
		else
		{
			this.Selection.Use = true;
		}

		return;
	}
	else if (Direction > 0)
	{
		Start = this.Selection.StartPos;
		End   = this.Selection.EndPos;
	}
	else
	{
		End   = this.Selection.StartPos;
		Start = this.Selection.EndPos;
	}

	// Чтобы не было эффекта, когда ничего не поселекчено, а при удалении соединяются параграфы
	if (Direction > 0 && type_Paragraph === this.Content[Start].GetType() && true === this.Content[Start].IsSelectionEmpty() && this.Content[Start].Selection.StartPos == this.Content[Start].Content.length - 1)
	{
		this.Content[Start].Selection.StartPos = this.Content[Start].Internal_GetEndPos();
		this.Content[Start].Selection.EndPos   = this.Content[Start].Content.length - 1;
	}

	var ElementPageIndex = this.private_GetElementPageIndexByXY(ContentPos, X, Y, this.CurPage);
	this.Content[ContentPos].Selection_SetEnd(X, Y, ElementPageIndex, MouseEvent);

	for (var Index = Start; Index <= End; Index++)
	{
		var Item = this.Content[Index];
		Item.SetSelectionUse(true);

		switch (Index)
		{
			case Start:

				Item.SetSelectionToBeginEnd(Direction > 0 ? false : true, false);
				break;

			case End:

				Item.SetSelectionToBeginEnd(Direction > 0 ? true : false, true);
				break;

			default:

				Item.SelectAll(Direction);
				break;
		}
	}
};
CDocumentContent.prototype.CheckPosInSelection = function(X, Y, CurPage, NearPos)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.DrawingObjects.selectionCheck(X, Y, this.Get_AbsolutePage(CurPage), NearPos);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (true === this.Selection.Use || true === this.ApplyToAll)
		{
			switch (this.Selection.Flag)
			{
				case selectionflag_Common:
				{
					var Start = this.Selection.StartPos;
					var End   = this.Selection.EndPos;

					if (Start > End)
					{
						Start = this.Selection.EndPos;
						End   = this.Selection.StartPos;
					}

					if (undefined !== NearPos)
					{
						if (true === this.ApplyToAll)
						{
							Start = 0;
							End   = this.Content.length - 1;
						}

						for (var Index = Start; Index <= End; Index++)
						{
							if (true === this.ApplyToAll)
								this.Content[Index].Set_ApplyToAll(true);

							if (true === this.Content[Index].CheckPosInSelection(0, 0, 0, NearPos))
							{
								if (true === this.ApplyToAll)
									this.Content[Index].Set_ApplyToAll(false);

								return true;
							}

							if (true === this.ApplyToAll)
								this.Content[Index].Set_ApplyToAll(false);
						}

						return false;
					}
					else
					{
						var ContentPos = this.Internal_GetContentPosByXY(X, Y, CurPage);
						if (ContentPos > Start && ContentPos < End)
						{
							return true;
						}
						else if (ContentPos < Start || ContentPos > End)
						{
							return false;
						}
						else
						{
							var ElementPageIndex = this.private_GetElementPageIndexByXY(ContentPos, X, Y, CurPage);
							return this.Content[ContentPos].CheckPosInSelection(X, Y, ElementPageIndex, NearPos);
						}

						return false;
					}
				}
				case selectionflag_Numbering :
					return false;
			}

			return false;
		}

		return false;
	}
};
CDocumentContent.prototype.IsSelectionEmpty = function(bCheckHidden)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.selectionIsEmpty(bCheckHidden);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (true === this.Selection.Use)
		{
			// Выделение нумерации
			if (selectionflag_Numbering == this.Selection.Flag)
				return false;
			// Обрабатываем движение границы у таблиц
			else if (null != this.Selection.Data && true === this.Selection.Data.TableBorder && type_Table == this.Content[this.Selection.Data.Pos].GetType())
				return false;
			else
			{
				if (this.Selection.StartPos === this.Selection.EndPos)
					return this.Content[this.Selection.StartPos].IsSelectionEmpty(bCheckHidden);
				else
					return false;
			}
		}

		return true;
	}
};
CDocumentContent.prototype.SelectAll = function()
{
	if (docpostype_DrawingObjects === this.CurPos.Type && true === this.DrawingObjects.isSelectedText())
	{
		this.DrawingObjects.selectAll();
	}
	else
	{
		if (true === this.Selection.Use)
			this.RemoveSelection();

		this.Set_DocPosType(docpostype_Content);
		this.Selection.Use   = true;
		this.Selection.Start = false;
		this.Selection.Flag  = selectionflag_Common;

		this.Selection.StartPos = 0;
		this.Selection.EndPos   = this.Content.length - 1;

		for (var Index = 0; Index < this.Content.length; Index++)
		{
			this.Content[Index].SelectAll();
		}
	}
};
CDocumentContent.prototype.SetSelectionUse = function(isUse)
{
	if (true === isUse)
		this.Selection.Use = true;
	else
		this.RemoveSelection();
};
CDocumentContent.prototype.SetSelectionToBeginEnd = function(isSelectionStart, isElementStart)
{
	if (this.Content.length <= 0)
		return;

	if (true === isElementStart)
	{
		this.Content[0].SetSelectionUse(true);
		this.Content[0].SetSelectionToBeginEnd(isSelectionStart, true);
		if (isSelectionStart)
			this.Selection.StartPos = 0;
		else
			this.Selection.EndPos = 0;
	}
	else
	{
		this.Content[this.Content.length - 1].SetSelectionUse(true);
		this.Content[this.Content.length - 1].SetSelectionToBeginEnd(isSelectionStart, false);

		if (isSelectionStart)
			this.Selection.StartPos = this.Content.length - 1;
		else
			this.Selection.EndPos = this.Content.length - 1;
	}
};
CDocumentContent.prototype.Select_DrawingObject      = function(Id)
{
    this.RemoveSelection();

    this.Parent.Set_CurrentElement(true, this.Get_StartPage_Absolute() + this.CurPage, this);

    // Прячем курсор
    this.DrawingDocument.TargetEnd();
    this.DrawingDocument.SetCurrentPage(this.Get_StartPage_Absolute() + this.CurPage);

    var HdrFtr = this.Is_HdrFtr(true);
    if (null != HdrFtr)
    {
        HdrFtr.Content.Set_DocPosType(docpostype_DrawingObjects);
        HdrFtr.Content.Selection.Use   = true;
        HdrFtr.Content.Selection.Start = false;

        this.LogicDocument.Selection.Use   = true;
        this.LogicDocument.Selection.Start = false;
    }
    else
    {
        this.LogicDocument.Set_DocPosType(docpostype_DrawingObjects);
        this.LogicDocument.Selection.Use   = true;
        this.LogicDocument.Selection.Start = false;
    }

    this.LogicDocument.DrawingObjects.selectById(Id, this.Get_StartPage_Absolute() + this.CurPage);

    // TODO: Пока сделаем так, в будущем надо сделать функцию, которая у родительского класса обновляет Select
    editor.WordControl.m_oLogicDocument.Document_UpdateSelectionState();
    editor.WordControl.m_oLogicDocument.Document_UpdateInterfaceState();
};
CDocumentContent.prototype.Document_SelectNumbering  = function(NumPr, Index)
{
    this.RemoveSelection();

    this.Selection.Use      = true;
    this.Selection.Flag     = selectionflag_Numbering;
    this.Selection.Data     = [];
    this.Selection.StartPos = Index;
    this.Selection.EndPos   = Index;

    for (var Index = 0; Index < this.Content.length; Index++)
    {
        var Item      = this.Content[Index];
        var ItemNumPr = null;
        if (type_Paragraph == Item.GetType() && undefined != ( ItemNumPr = Item.Numbering_Get() ) && ItemNumPr.NumId == NumPr.NumId && ItemNumPr.Lvl == NumPr.Lvl)
        {
            this.Selection.Data.push(Index);
            Item.Selection_SelectNumbering();
        }
    }

    this.DrawingDocument.SelectEnabled(true);

    this.LogicDocument.Document_UpdateSelectionState();

    this.Interface_Update_ParaPr();
    this.Interface_Update_TextPr();
};
// Если сейчас у нас заселекчена нумерация, тогда убираем селект
CDocumentContent.prototype.Remove_NumberingSelection = function()
{
    if (true === this.Selection.Use && selectionflag_Numbering == this.Selection.Flag)
        this.RemoveSelection();
};
//-----------------------------------------------------------------------------------
// Функции для работы с таблицами
//-----------------------------------------------------------------------------------
CDocumentContent.prototype.AddTableRow = function(bBefore)
{
	if (docpostype_DrawingObjects == this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.tableAddRow(bBefore);
	}
	else if (docpostype_Content == this.CurPos.Type && ( ( true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType() ) || ( false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType() ) ))
	{
		var Pos = 0;
		if (true === this.Selection.Use)
			Pos = this.Selection.StartPos;
		else
			Pos = this.CurPos.ContentPos;

		this.Content[Pos].AddTableRow(bBefore);
		if (false === this.Selection.Use && true === this.Content[Pos].IsSelectionUse())
		{
			this.Selection.Use      = true;
			this.Selection.StartPos = Pos;
			this.Selection.EndPos   = Pos;
		}

		return true;
	}

	return false;
};
CDocumentContent.prototype.AddTableColumn = function(bBefore)
{
	if (docpostype_DrawingObjects == this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.tableAddCol(bBefore);
	}
	else if (docpostype_Content == this.CurPos.Type && ( ( true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType() ) || ( false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType() ) ))
	{
		var Pos = 0;
		if (true === this.Selection.Use)
			Pos = this.Selection.StartPos;
		else
			Pos = this.CurPos.ContentPos;

		this.Content[Pos].AddTableColumn(bBefore);
		if (false === this.Selection.Use && true === this.Content[Pos].IsSelectionUse())
		{
			this.Selection.Use      = true;
			this.Selection.StartPos = Pos;
			this.Selection.EndPos   = Pos;
		}

		return true;
	}

	return false;
};
CDocumentContent.prototype.RemoveTableRow = function()
{
	if (docpostype_DrawingObjects == this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.tableRemoveRow();
	}
	else if (docpostype_Content == this.CurPos.Type && ( ( true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType() ) || ( false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType() ) ))
	{
		var Pos = 0;
		if (true === this.Selection.Use)
			Pos = this.Selection.StartPos;
		else
			Pos = this.CurPos.ContentPos;

		if (false === this.Content[Pos].RemoveTableRow())
			this.RemoveTable();

		return true;
	}

	return false;
};
CDocumentContent.prototype.RemoveTableColumn = function()
{
	if (docpostype_DrawingObjects == this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.tableRemoveCol();
	}
	else if (docpostype_Content == this.CurPos.Type && ( ( true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType() ) || ( false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType() ) ))
	{
		var Pos = 0;
		if (true === this.Selection.Use)
			Pos = this.Selection.StartPos;
		else
			Pos = this.CurPos.ContentPos;

		if (false === this.Content[Pos].RemoveTableColumn())
			this.RemoveTable();

		return true;
	}

	return false;
};
CDocumentContent.prototype.MergeTableCells = function()
{
	if (docpostype_DrawingObjects == this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.tableMergeCells();
	}
	else if (docpostype_Content == this.CurPos.Type && ( ( true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType() ) || ( false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType() ) ))
	{
		var Pos = 0;
		if (true === this.Selection.Use)
			Pos = this.Selection.StartPos;
		else
			Pos = this.CurPos.ContentPos;

		this.Content[Pos].MergeTableCells();
		return true;
	}

	return false;
};
CDocumentContent.prototype.SplitTableCells = function(Cols, Rows)
{
	if (docpostype_DrawingObjects == this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.tableSplitCell();
	}
	else if (docpostype_Content == this.CurPos.Type && ( ( true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType() ) || ( false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType() ) ))
	{
		var Pos = 0;
		if (true === this.Selection.Use)
			Pos = this.Selection.StartPos;
		else
			Pos = this.CurPos.ContentPos;

		this.Content[Pos].SplitTableCells(Rows, Cols);
		return true;
	}

	return false;
};
CDocumentContent.prototype.RemoveTable = function()
{
    if (docpostype_DrawingObjects == this.CurPos.Type)
    {
        return this.LogicDocument.DrawingObjects.tableRemoveTable();
    }
    else if (docpostype_Content == this.CurPos.Type && ( ( true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType() ) || ( false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType() ) ))
    {
        var Pos;
        if (true === this.Selection.Use)
            Pos = this.Selection.StartPos;
        else
            Pos = this.CurPos.ContentPos;

        var Table = this.Content[Pos];
        if (type_Table === Table.GetType())
		{
			if (true === Table.IsInnerTable())
			{
				Table.RemoveInnerTable();
			}
			else
			{
				this.RemoveSelection();
				Table.PreDelete();
				this.Internal_Content_Remove(Pos, 1);

				if (Pos >= this.Content.length - 1)
					Pos--;

				if (Pos < 0)
					Pos = 0;

				this.Set_DocPosType(docpostype_Content);
				this.CurPos.ContentPos = Pos;
				this.Content[Pos].MoveCursorToStartPos();
			}

			return true;
		}
		else
		{
			return Table.RemoveTable();
		}
    }
    return false;
};
CDocumentContent.prototype.SelectTable = function(Type)
{
	if (docpostype_DrawingObjects == this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.tableSelect(Type);
	}
	else if (docpostype_Content == this.CurPos.Type && ( ( true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType() ) || ( false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType() ) ))
	{
		var Pos = 0;
		if (true === this.Selection.Use)
			Pos = this.Selection.StartPos;
		else
			Pos = this.CurPos.ContentPos;

		this.Content[Pos].SelectTable(Type);
		if (false === this.Selection.Use && true === this.Content[Pos].IsSelectionUse())
		{
			this.Selection.Use      = true;
			this.Selection.StartPos = Pos;
			this.Selection.EndPos   = Pos;
		}
		return true;
	}

	return false;
};
CDocumentContent.prototype.CanMergeTableCells = function()
{
	if (docpostype_DrawingObjects == this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.tableCheckMerge();
	}
	else if (docpostype_Content == this.CurPos.Type && ( ( true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType() ) || ( false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType() ) ))
	{
		var Pos = 0;
		if (true === this.Selection.Use)
			Pos = this.Selection.StartPos;
		else
			Pos = this.CurPos.ContentPos;

		return this.Content[Pos].CanMergeTableCells();
	}

	return false;
};
CDocumentContent.prototype.CanSplitTableCells = function()
{
	if (docpostype_DrawingObjects == this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.tableCheckSplit();
	}
	else if (docpostype_Content == this.CurPos.Type && ( ( true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType() ) || ( false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType() ) ))
	{
		var Pos = 0;
		if (true === this.Selection.Use)
			Pos = this.Selection.StartPos;
		else
			Pos = this.CurPos.ContentPos;

		return this.Content[Pos].CanSplitTableCells();
	}

	return false;
};
//-----------------------------------------------------------------------------------
// Вспомогательные(внутренние ) функции
//-----------------------------------------------------------------------------------
CDocumentContent.prototype.Internal_GetContentPosByXY = function(X, Y, PageNum)
{
    if (undefined === PageNum || null === PageNum)
        PageNum = this.CurPage;

    PageNum = Math.max(0, Math.min(PageNum, this.Pages.length - 1));

    // Сначала проверим Flow-таблицы
    var FlowTable = this.LogicDocument && this.LogicDocument.DrawingObjects.getTableByXY(X, Y, PageNum + this.Get_StartPage_Absolute(), this);
    if (null != FlowTable)
        return FlowTable.Table.Index;

    // Теперь проверим пустые параграфы с окончанием секций (в нашем случае это пустой параграф послей таблицы внутри таблицы)
    var SectCount = this.Pages[PageNum].EndSectionParas.length;
    for (var Index = 0; Index < SectCount; ++Index)
    {
        var Item   = this.Pages[PageNum].EndSectionParas[Index];
        var Bounds = Item.Pages[0].Bounds;

        if (Y < Bounds.Bottom && Y > Bounds.Top && X > Bounds.Left && X < Bounds.Right)
            return Item.Index;
    }

    var StartPos = Math.min(this.Pages[PageNum].Pos, this.Content.length - 1);
    var EndPos   = this.Content.length - 1;

    if (PageNum < this.Pages.length - 1)
        EndPos = Math.min(this.Pages[PageNum + 1].Pos, EndPos);

    // Сохраним позиции всех Inline элементов на данной странице
    var InlineElements = [];
    for (var Index = StartPos; Index <= EndPos; Index++)
    {
        var Item = this.Content[Index];
        var bEmptySectPara = this.Pages[PageNum].Check_EndSectionPara(Item);

        if (false != Item.Is_Inline() && (type_Paragraph !== Item.GetType() || false === bEmptySectPara))
            InlineElements.push(Index);
    }

    var Count = InlineElements.length;
    if (Count <= 0)
        return StartPos;

    for (var Pos = 0; Pos < Count - 1; Pos++)
    {
        var Item = this.Content[InlineElements[Pos + 1]];

		var PageBounds = Item.GetPageBounds(0);
		if (Y < PageBounds.Top)
			return InlineElements[Pos];

        if (Item.GetPagesCount() > 1)
        {
            if (true !== Item.IsStartFromNewPage())
                return InlineElements[Pos + 1];

            return InlineElements[Pos];
        }

        if (Pos === Count - 2)
        {
            // Такое возможно, если страница заканчивается Flow-таблицей
            return InlineElements[Count - 1];
        }
    }

    return InlineElements[0];
};
CDocumentContent.prototype.private_CheckCurPage = function()
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		// TODO: переделать
		this.CurPage = 0;
	}
	else if (docpostype_Content === this.CurPos.Type)
	{
		if (true === this.Selection.Use)
		{
			this.CurPage = this.Content[this.Selection.EndPos].Get_CurrentPage_Relative();
		}
		else if (this.CurPos.ContentPos >= 0)
		{
			this.CurPage = this.Content[this.CurPos.ContentPos].Get_CurrentPage_Relative();
		}
	}
};
CDocumentContent.prototype.Internal_Content_Add = function(Position, NewObject, bCheckLastElement)
{
	// Position = this.Content.length  допускается
	if (Position < 0 || Position > this.Content.length)
		return;

	var PrevObj = this.Content[Position - 1] ? this.Content[Position - 1] : null;
	var NextObj = this.Content[Position] ? this.Content[Position] : null;

	this.private_RecalculateNumbering([NewObject]);
	History.Add(new CChangesDocumentContentAddItem(this, Position, [NewObject]));
	this.Content.splice(Position, 0, NewObject);
	NewObject.Set_Parent(this);
	NewObject.Set_DocumentNext(NextObj);
	NewObject.Set_DocumentPrev(PrevObj);

	if (null != PrevObj)
		PrevObj.Set_DocumentNext(NewObject);

	if (null != NextObj)
		NextObj.Set_DocumentPrev(NewObject);

	if (Position <= this.CurPos.TableMove)
		this.CurPos.TableMove++;

	// Проверим, что последний элемент - параграф
	if (false != bCheckLastElement && type_Paragraph !== this.Content[this.Content.length - 1].GetType())
		this.Internal_Content_Add(this.Content.length, new Paragraph(this.DrawingDocument, this, this.bPresentation === true));

	this.private_ReindexContent(Position);
};
CDocumentContent.prototype.Internal_Content_Remove = function(Position, Count, bCheckLastElement)
{
	if (Position < 0 || Position >= this.Content.length || Count <= 0)
		return;

	var PrevObj = this.Content[Position - 1] ? this.Content[Position - 1] : null;
	var NextObj = this.Content[Position + Count] ? this.Content[Position + Count] : null;

	for (var Index = 0; Index < Count; Index++)
		this.Content[Position + Index].PreDelete();

	History.Add(new CChangesDocumentContentRemoveItem(this, Position, this.Content.slice(Position, Position + Count)));
	var Elements = this.Content.splice(Position, Count);
	this.private_RecalculateNumbering(Elements);

	if (null != PrevObj)
		PrevObj.Set_DocumentNext(NextObj);

	if (null != NextObj)
		NextObj.Set_DocumentPrev(PrevObj);

	// Проверим, что последний элемент - параграф
	if (false !== bCheckLastElement && (this.Content.length <= 0 || type_Paragraph !== this.Content[this.Content.length - 1].GetType()))
		this.Internal_Content_Add(this.Content.length, new Paragraph(this.DrawingDocument, this, this.bPresentation === true));

	this.private_ReindexContent(Position);
};
CDocumentContent.prototype.Clear_ContentChanges = function()
{
	this.m_oContentChanges.Clear();
};
CDocumentContent.prototype.Add_ContentChanges = function(Changes)
{
	this.m_oContentChanges.Add(Changes);
};
CDocumentContent.prototype.Refresh_ContentChanges = function()
{
	this.m_oContentChanges.Refresh();
};
CDocumentContent.prototype.Internal_Content_RemoveAll = function()
{
	var Count = this.Content.length;
	for (var Index = 0; Index < Count; Index++)
		this.Content[Index].PreDelete();

	History.Add(new CChangesDocumentRemoveItem(this, 0, this.Content.slice(0, this.Content.length)));
	this.Content = [];
};
//-----------------------------------------------------------------------------------
// Функции для работы с номерами страниц
//-----------------------------------------------------------------------------------
CDocumentContent.prototype.Get_StartPage_Absolute = function()
{
	return this.Get_AbsolutePage(0);
};
CDocumentContent.prototype.Get_StartPage_Relative = function()
{
	return this.StartPage;
};
CDocumentContent.prototype.Get_StartColumn_Absolute = function()
{
	return this.Get_AbsoluteColumn(0);
};
CDocumentContent.prototype.Set_StartPage = function(StartPage, StartColumn, ColumnsCount)
{
	this.StartPage    = StartPage;
	this.StartColumn  = undefined !== StartColumn ? StartColumn : 0;
	this.ColumnsCount = undefined !== ColumnsCount ? ColumnsCount : 1;
};
CDocumentContent.prototype.Get_ColumnsCount = function()
{
	return this.ColumnsCount;
};
CDocumentContent.prototype.private_GetRelativePageIndex = function(CurPage)
{
	if (!this.ColumnsCount || 0 === this.ColumnsCount)
		return this.StartPage + CurPage;

	return this.StartPage + ((this.StartColumn + CurPage) / this.ColumnsCount | 0);
};
CDocumentContent.prototype.private_GetAbsolutePageIndex = function(CurPage)
{
	return this.Parent.Get_AbsolutePage(this.private_GetRelativePageIndex(CurPage));
};
CDocumentContent.prototype.Get_StartColumn = function()
{
	return this.StartColumn;
};
CDocumentContent.prototype.Get_AbsolutePage = function(CurPage)
{
	return this.private_GetAbsolutePageIndex(CurPage);
};
CDocumentContent.prototype.Get_AbsoluteColumn = function(CurPage)
{
	return this.private_GetColumnIndex(CurPage);
};
CDocumentContent.prototype.private_GetColumnIndex = function(CurPage)
{
	// TODO: Разобраться здесь нужно ли данное условие. Оно появилось из-за параграфов в таблице в
	//       основной части документа и из-за параграфов в сносках.
	if (1 === this.ColumnsCount)
    	return this.Parent.Get_AbsoluteColumn(this.private_GetRelativePageIndex(CurPage));

	return (this.StartColumn + CurPage) - (((this.StartColumn + CurPage) / this.ColumnsCount | 0) * this.ColumnsCount);
};
//-----------------------------------------------------------------------------------
// Undo/Redo функции
//-----------------------------------------------------------------------------------
CDocumentContent.prototype.GetSelectionState = function()
{
	var DocState    = {};
	DocState.CurPos = {
		X          : this.CurPos.X,
		Y          : this.CurPos.Y,
		ContentPos : this.CurPos.ContentPos,
		RealX      : this.CurPos.RealX,
		RealY      : this.CurPos.RealY,
		Type       : this.CurPos.Type
	};

	DocState.Selection = {

		Start    : this.Selection.Start,
		Use      : this.Selection.Use,
		StartPos : this.Selection.StartPos,
		EndPos   : this.Selection.EndPos,
		Flag     : this.Selection.Flag,
		Data     : this.Selection.Data
	};

	DocState.CurPage = this.CurPage;

	var State = null;

	if (this.LogicDocument && true === editor.isStartAddShape && docpostype_DrawingObjects === this.CurPos.Type)
	{
		DocState.CurPos.Type     = docpostype_Content;
		DocState.Selection.Start = false;
		DocState.Selection.Use   = false;

		this.Content[DocState.CurPos.ContentPos].RemoveSelection();
		State = this.Content[this.CurPos.ContentPos].GetSelectionState();
	}
	else
	{
		// Работаем с колонтитулом
		if (docpostype_DrawingObjects === this.CurPos.Type)
			State = this.LogicDocument.DrawingObjects.getSelectionState();
		else if (docpostype_Content === this.CurPos.Type)
		{
			if (true === this.Selection.Use)
			{
				// Выделение нумерации
				if (selectionflag_Numbering == this.Selection.Flag)
					State = [];
				else
				{
					var StartPos = this.Selection.StartPos;
					var EndPos   = this.Selection.EndPos;
					if (StartPos > EndPos)
					{
						var Temp = StartPos;
						StartPos = EndPos;
						EndPos   = Temp;
					}

					State = [];

					var TempState = [];
					for (var Index = StartPos; Index <= EndPos; Index++)
					{
						TempState.push(this.Content[Index].GetSelectionState());
					}

					State.push(TempState);
				}
			}
			else
				State = this.Content[this.CurPos.ContentPos].GetSelectionState();
		}
	}

	if (null != this.Selection.Data && true === this.Selection.Data.TableBorder)
	{
		DocState.Selection.Data = null;
	}

	State.push(DocState);
	return State;
};
CDocumentContent.prototype.SetSelectionState = function(State, StateIndex)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
		this.LogicDocument.DrawingObjects.resetSelection();

	if (State.length <= 0)
		return;

	var DocState = State[StateIndex];

	this.CurPos = {
		X          : DocState.CurPos.X,
		Y          : DocState.CurPos.Y,
		ContentPos : DocState.CurPos.ContentPos,
		RealX      : DocState.CurPos.RealX,
		RealY      : DocState.CurPos.RealY,
		Type       : DocState.CurPos.Type
	};

	this.Set_DocPosType(DocState.CurPos.Type);

	this.Selection = {

		Start    : DocState.Selection.Start,
		Use      : DocState.Selection.Use,
		StartPos : DocState.Selection.StartPos,
		EndPos   : DocState.Selection.EndPos,
		Flag     : DocState.Selection.Flag,
		Data     : DocState.Selection.Data
	};

	this.CurPage = DocState.CurPage;

	var NewStateIndex = StateIndex - 1;

	// Работаем с колонтитулом
	if (docpostype_DrawingObjects == this.CurPos.Type)
	{
		this.LogicDocument.DrawingObjects.setSelectionState(State, NewStateIndex);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (true === this.Selection.Use)
		{
			if (selectionflag_Numbering == this.Selection.Flag)
			{
				if (type_Paragraph === this.Content[this.Selection.StartPos].Get_Type())
				{
					var NumPr = this.Content[this.Selection.StartPos].Numbering_Get();
					if (undefined !== NumPr)
						this.Document_SelectNumbering(NumPr, this.Selection.StartPos);
					else
						this.LogicDocument.RemoveSelection();
				}
				else
					this.LogicDocument.RemoveSelection();
			}
			else
			{
				var StartPos = this.Selection.StartPos;
				var EndPos   = this.Selection.EndPos;
				if (StartPos > EndPos)
				{
					var Temp = StartPos;
					StartPos = EndPos;
					EndPos   = Temp;
				}

				var CurState = State[NewStateIndex];

				for (var Index = StartPos; Index <= EndPos; Index++)
				{
					this.Content[Index].SetSelectionState(CurState[Index - StartPos], CurState[Index - StartPos].length - 1);
				}
			}
		}
		else
		{
			this.Content[this.CurPos.ContentPos].SetSelectionState(State, NewStateIndex);
		}
	}
};
CDocumentContent.prototype.Get_ParentObject_or_DocumentPos = function()
{
    return this.Parent.Get_ParentObject_or_DocumentPos();
};
CDocumentContent.prototype.Refresh_RecalcData = function(Data)
{
	var bNeedRecalc = false;

	var Type = Data.Type;

	var CurPage = 0;

	switch (Type)
	{
		case AscDFH.historyitem_DocumentContent_AddItem:
		case AscDFH.historyitem_DocumentContent_RemoveItem:
		{
			for (CurPage = this.Pages.length - 1; CurPage > 0; CurPage--)
			{
				if (Data.Pos > this.Pages[CurPage].Pos)
					break;
			}

			bNeedRecalc = true;
			break;
		}
	}

	this.Refresh_RecalcData2(0, CurPage);
};
CDocumentContent.prototype.Refresh_RecalcData2 = function(Index, Page_rel)
{
	this.Parent.Refresh_RecalcData2(this.StartPage + Page_rel);
};
//-----------------------------------------------------------------------------------
// Функции для работы с гиперссылками
//-----------------------------------------------------------------------------------
CDocumentContent.prototype.AddHyperlink = function(HyperProps)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.hyperlinkAdd(HyperProps);
	}
	else if (docpostype_Content === this.CurPos.Type
		&& (false === this.Selection.Use || this.Selection.StartPos === this.Selection.EndPos))
	{
		var Pos = ( true == this.Selection.Use ? this.Selection.StartPos : this.CurPos.ContentPos );
		this.Content[Pos].AddHyperlink(HyperProps);
	}
};
CDocumentContent.prototype.ModifyHyperlink = function(HyperProps)
{
	if (docpostype_DrawingObjects == this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.hyperlinkModify(HyperProps);
	}
	else if (docpostype_Content == this.CurPos.Type
		&& (false === this.Selection.Use || this.Selection.StartPos === this.Selection.EndPos))
	{
		var Pos = ( true == this.Selection.Use ? this.Selection.StartPos : this.CurPos.ContentPos );
		this.Content[Pos].ModifyHyperlink(HyperProps);
	}
};
CDocumentContent.prototype.RemoveHyperlink = function()
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.hyperlinkRemove();
	}
	else if (docpostype_Content == this.CurPos.Type
		&& (false === this.Selection.Use || this.Selection.StartPos === this.Selection.EndPos))
	{
		var Pos = ( true == this.Selection.Use ? this.Selection.StartPos : this.CurPos.ContentPos );
		this.Content[Pos].RemoveHyperlink();
	}
};
CDocumentContent.prototype.CanAddHyperlink = function(bCheckInHyperlink)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.hyperlinkCanAdd(bCheckInHyperlink);
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (true === this.Selection.Use)
		{
			switch (this.Selection.Flag)
			{
				case selectionflag_Numbering:
					return false;
				case selectionflag_Common:
				{
					if (this.Selection.StartPos != this.Selection.EndPos)
						return false;

					return this.Content[this.Selection.StartPos].CanAddHyperlink(bCheckInHyperlink);
				}
			}
		}
		else
			return this.Content[this.CurPos.ContentPos].CanAddHyperlink(bCheckInHyperlink);
	}

	return false;
};
CDocumentContent.prototype.IsCursorInHyperlink = function(bCheckEnd)
{
	if (docpostype_DrawingObjects == this.CurPos.Type)
	{
		return this.LogicDocument.DrawingObjects.hyperlinkCheck(bCheckEnd);
	}
	else //if ( docpostype_Content == this.CurPos.Type )
	{
		if (true === this.Selection.Use)
		{
			switch (this.Selection.Flag)
			{
				case selectionflag_Numbering:
					return null;
				case selectionflag_Common:
				{
					if (this.Selection.StartPos != this.Selection.EndPos)
						return null;

					return this.Content[this.Selection.StartPos].IsCursorInHyperlink(bCheckEnd);
				}
			}
		}
		else
		{
			return this.Content[this.CurPos.ContentPos].IsCursorInHyperlink(bCheckEnd);
		}
	}

	return null;
};
//-----------------------------------------------------------------------------------
// Функции для работы с совместным редактирования
//-----------------------------------------------------------------------------------
CDocumentContent.prototype.Write_ToBinary2 = function(Writer)
{
	Writer.WriteLong(AscDFH.historyitem_type_DocumentContent);

	// String : Id текущего элемента
	// Long   : StartPage
	// String : Id родительского класса
	// Bool   : TurnOffInnerWrap
	// Bool   : Split
	// Long   : Количество элементов в массиве this.Content
	// Array of string : массив Id элементов

	Writer.WriteString2(this.Id);
	Writer.WriteLong(this.StartPage);
	Writer.WriteString2(this.Parent.Get_Id());
	Writer.WriteBool(this.TurnOffInnerWrap);
	Writer.WriteBool(this.Split);
	AscFormat.writeBool(Writer, this.bPresentation);


	var ContentToWrite;
	if (this.StartState)
	{
		ContentToWrite = this.StartState.Content;
	}
	else
	{
		ContentToWrite = this.Content;
	}

	var Count = ContentToWrite.length;
	Writer.WriteLong(Count);
	for (var Index = 0; Index < Count; Index++)
		Writer.WriteString2(ContentToWrite[Index].Get_Id());

	if (this.Parent && this.Parent.Get_Worksheet)
	{
		Writer.WriteBool(true);
		var worksheet = this.Parent.Get_Worksheet();
		if (worksheet)
		{
			Writer.WriteBool(true);
			Writer.WriteString2(worksheet.getId())
		}
		else
		{
			Writer.WriteBool(false);
		}
	}
	else
	{
		Writer.WriteBool(false);
	}
};
CDocumentContent.prototype.Read_FromBinary2 = function(Reader)
{
	// String : Id текущего элемента
	// Long   : StartPage
	// String : Id родительского класса
	// Bool   : TurnOffInnerWrap
	// Bool   : Split
	// Long   : Количество элементов в массиве this.Content
	// Array of string : массив Id элементов

	var LinkData = {};

	this.Id               = Reader.GetString2();
	this.StartPage        = Reader.GetLong();
	LinkData.Parent       = Reader.GetString2();
	this.TurnOffInnerWrap = Reader.GetBool();
	this.Split            = Reader.GetBool();
	this.bPresentation    = AscFormat.readBool(Reader);

	var Count    = Reader.GetLong();
	this.Content = [];
	for (var Index = 0; Index < Count; Index++)
	{
		var Element = g_oTableId.Get_ById(Reader.GetString2());
		if (null != Element)
		{
			this.Content.push(Element);
			Element.Parent = this;
		}
	}

	AscCommon.CollaborativeEditing.Add_LinkData(this, LinkData);

	var b_worksheet = Reader.GetBool();
	if (b_worksheet)
	{
		this.Parent        = g_oTableId.Get_ById(LinkData.Parent);
		var b_worksheet_id = Reader.GetBool();
		if (b_worksheet_id)
		{
			var id  = Reader.GetString2();
			var api = window["Asc"]["editor"];
			if (api.wb)
			{
				var worksheet = api.wbModel.getWorksheetById(id);
				if (worksheet)
				{
					this.DrawingDocument = worksheet.DrawingDocument;
				}
			}
		}
	}
	else
	{
		var DrawingDocument;
		if (editor && editor.WordControl && editor.WordControl.m_oDrawingDocument)
			DrawingDocument = editor.WordControl.m_oDrawingDocument;
		if (undefined !== DrawingDocument && null !== DrawingDocument)
		{
			this.DrawingDocument = DrawingDocument;

			if (undefined !== editor && true === editor.isDocumentEditor)
			{
				this.LogicDocument  = DrawingDocument.m_oLogicDocument;
				this.Styles         = DrawingDocument.m_oLogicDocument.Get_Styles();
				this.Numbering      = DrawingDocument.m_oLogicDocument.Get_Numbering();
				this.DrawingObjects = DrawingDocument.m_oLogicDocument.DrawingObjects; // Массив укзателей на все инлайновые графические объекты
			}
		}
	}
};
CDocumentContent.prototype.Load_LinkData = function(LinkData)
{
	if ("undefined" != typeof(LinkData.Parent))
		this.Parent = g_oTableId.Get_ById(LinkData.Parent);

	if (this.Parent.getDrawingDocument)
	{
		this.DrawingDocument = this.Parent.getDrawingDocument();
		for (var i = 0; i < this.Content.length; ++i)
		{
			this.Content[i].DrawingDocument = this.DrawingDocument;
		}
	}
};
CDocumentContent.prototype.Get_SelectionState2 = function()
{
    // Сохраняем Id ближайшего элемента в текущем классе
    var State = new CDocumentSelectionState();

    State.Id   = this.Get_Id();
    State.Type = docpostype_Content;

    var Element = this.Content[this.CurPos.ContentPos];
    State.Data  = Element.Get_SelectionState2();

    return State;
};
CDocumentContent.prototype.Set_SelectionState2 = function(State)
{
    var ElementId = State.Data.Id;

    var CurId = ElementId;

    var bFlag = false;

    var Pos = 0;

    // Найдем элемент с Id = CurId
    var Count = this.Content.length;
    for (Pos = 0; Pos < Count; Pos++)
    {
        if (this.Content[Pos].Get_Id() == CurId)
        {
            bFlag = true;
            break;
        }
    }

    if (true !== bFlag)
    {
        var TempElement = g_oTableId.Get_ById(CurId);
        Pos             = ( null != TempElement ? Math.min(this.Content.length - 1, TempElement.Index) : 0 );
    }

    this.Selection.Start    = false;
    this.Selection.Use      = false;
    this.Selection.StartPos = Pos;
    this.Selection.EndPos   = Pos;
    this.Selection.Flag     = selectionflag_Common;

    this.Set_DocPosType(docpostype_Content);
    this.CurPos.ContentPos = Pos;

    if (true !== bFlag)
        this.Content[this.CurPos.ContentPos].MoveCursorToStartPos();
    else
    {
        this.Content[this.CurPos.ContentPos].Set_SelectionState2(State.Data);
    }
};
//-----------------------------------------------------------------------------------
// Функции для работы с комментариями
//-----------------------------------------------------------------------------------
CDocumentContent.prototype.AddComment = function(Comment, bStart, bEnd)
{
	if (true === this.ApplyToAll)
	{
		if (this.Content.length <= 1 && true === bStart && true === bEnd)
		{
			this.Content[0].Set_ApplyToAll(true);
			this.Content[0].AddComment(Comment, true, true);
			this.Content[0].Set_ApplyToAll(false);
		}
		else
		{
			if (true === bStart)
			{
				this.Content[0].Set_ApplyToAll(true);
				this.Content[0].AddComment(Comment, true, false);
				this.Content[0].Set_ApplyToAll(false);
			}

			if (true === bEnd)
			{
				this.Content[this.Content.length - 1].Set_ApplyToAll(true);
				this.Content[this.Content.length - 1].AddComment(Comment, false, true);
				this.Content[this.Content.length - 1].Set_ApplyToAll(true);
			}
		}
	}
	else
	{
		if (docpostype_DrawingObjects === this.CurPos.Type)
		{
			return this.LogicDocument.DrawingObjects.addComment(Comment);
		}
		else //if ( docpostype_Content === this.CurPos.Type )
		{
			if (selectionflag_Numbering === this.Selection.Flag)
				return;

			if (true === this.Selection.Use)
			{
				var StartPos, EndPos;
				if (this.Selection.StartPos < this.Selection.EndPos)
				{
					StartPos = this.Selection.StartPos;
					EndPos   = this.Selection.EndPos;
				}
				else
				{
					StartPos = this.Selection.EndPos;
					EndPos   = this.Selection.StartPos;
				}

				if (StartPos === EndPos)
					this.Content[StartPos].AddComment(Comment, bStart, bEnd);
				else
				{
					if (true === bStart)
						this.Content[StartPos].AddComment(Comment, true, false);

					if (true === bEnd)
						this.Content[EndPos].AddComment(Comment, false, true);
				}
			}
			else
			{
				this.Content[this.CurPos.ContentPos].AddComment(Comment, bStart, bEnd);
			}
		}
	}
};
CDocumentContent.prototype.CanAddComment = function()
{
	if (true === this.ApplyToAll)
	{
		if (this.Content.length > 1)
			return true;
		else
			return this.Content[0].CanAddComment();
	}
	else
	{
		if (docpostype_DrawingObjects === this.CurPos.Type)
		{
			if (true != this.LogicDocument.DrawingObjects.isSelectedText())
				return true;
			else
				return this.LogicDocument.DrawingObjects.canAddComment();
		}
		else //if ( docpostype_Content === this.CurPos.Type )
		{
			switch (this.Selection.Flag)
			{
				case selectionflag_Numbering:
					return false;
				case selectionflag_Common:
				{
					if (true === this.Selection.Use && this.Selection.StartPos != this.Selection.EndPos)
						return true;
					else
					{
						var Pos     = ( this.Selection.Use === true ? this.Selection.StartPos : this.CurPos.ContentPos );
						var Element = this.Content[Pos];
						return Element.CanAddComment();
					}
				}
			}
		}
	}

	return false;
};
CDocumentContent.prototype.GetSelectionBounds = function()
{
	if (true === this.Selection.Use && selectionflag_Common === this.Selection.Flag)
	{
		var Start = this.Selection.StartPos;
		var End   = this.Selection.EndPos;

		if (Start > End)
		{
			Start = this.Selection.EndPos;
			End   = this.Selection.StartPos;
		}

		if (Start === End)
			return this.Content[Start].GetSelectionBounds();
		else
		{
			var Result       = {};
			Result.Start     = this.Content[Start].GetSelectionBounds().Start;
			Result.End       = this.Content[End].GetSelectionBounds().End;
			Result.Direction = (this.Selection.StartPos > this.Selection.EndPos ? -1 : 1);
			return Result;
		}
	}

	return null;
};
CDocumentContent.prototype.GetSelectionAnchorPos = function()
{
	var Pos = ( true === this.Selection.Use ? ( this.Selection.StartPos < this.Selection.EndPos ? this.Selection.StartPos : this.Selection.EndPos ) : this.CurPos.ContentPos );
	return this.Content[Pos].GetSelectionAnchorPos();
};
CDocumentContent.prototype.GetEndInfo = function()
{
	var ContentLen = this.Content.length;
	if (ContentLen > 0)
		return this.Content[ContentLen - 1].GetEndInfo();
	else
		return null;
};
CDocumentContent.prototype.GetPrevElementEndInfo = function(CurElement)
{
	var PrevElement = CurElement.Get_DocumentPrev();

	if (null !== PrevElement && undefined !== PrevElement)
	{
		return PrevElement.GetEndInfo();
	}
	else
	{
		return this.Parent.GetPrevElementEndInfo(this);
	}
};
CDocumentContent.prototype.GetTopElement = function()
{
    if (this.Parent)
        return this.Parent.GetTopElement();

    return null;
};
CDocumentContent.prototype.CompareDrawingsLogicPositions = function(CompareObject)
{
    for (var Index = 0, Count = this.Content.length; Index < Count; Index++)
    {
        var Element = this.Content[Index];
        Element.CompareDrawingsLogicPositions(CompareObject);

        if (0 !== CompareObject.Result)
            return;
    }
};
CDocumentContent.prototype.StartSelectionFromCurPos = function()
{
    if (docpostype_DrawingObjects === this.CurPos.Type)
    {
        return this.DrawingObjects.startSelectionFromCurPos();
    }
    else //if (docpostype_Content === this.CurPos.Type)
    {
        this.Selection.Use      = true;
        this.Selection.Start    = false;
        this.Selection.StartPos = this.CurPos.ContentPos;
        this.Selection.EndPos   = this.CurPos.ContentPos;
        this.Content[this.CurPos.ContentPos].StartSelectionFromCurPos();
    }
};
CDocumentContent.prototype.GetStyleFromFormatting = function()
{
    if (docpostype_DrawingObjects === this.CurPos.Type)
    {
        return this.DrawingObjects.GetStyleFromFormatting();
    }
    else //if (docpostype_Content === this.CurPos.Type)
    {
        if (true == this.Selection.Use)
        {
            if (this.Selection.StartPos > this.Selection.EndPos)
                return this.Content[this.Selection.EndPos].GetStyleFromFormatting();
            else
                return this.Content[this.Selection.StartPos].GetStyleFromFormatting();
        }
        else
        {
            return this.Content[this.CurPos.ContentPos].GetStyleFromFormatting();
        }
    }
};
CDocumentContent.prototype.Is_TrackRevisions = function()
{
    if (this.LogicDocument)
        return this.LogicDocument.Is_TrackRevisions();

    return false;
};
CDocumentContent.prototype.Get_SectPr = function()
{
    if (this.Parent && this.Parent.Get_SectPr)
        return this.Parent.Get_SectPr();

    return null;
};
CDocumentContent.prototype.SetParagraphFramePr = function(FramePr, bDelete)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		// Не добавляем и не работаем с рамками в автофигурах
		return;
	}
	else //if ( docpostype_Content === this.CurPos.Type )
	{
		if (true === this.Selection.Use)
		{
			// Проверим, если у нас все выделенные элементы - параграфы, с одинаковыми настройками
			// FramePr, тогда мы можем применить новую настройку FramePr

			var StartPos = this.Selection.StartPos;
			var EndPos   = this.Selection.EndPos;

			if (StartPos > EndPos)
			{
				StartPos = this.Selection.EndPos;
				EndPos   = this.Selection.StartPos;
			}

			var Element = this.Content[StartPos];

			if (type_Paragraph !== Element.GetType() || undefined === Element.Get_FramePr())
				return;

			var FramePr = Element.Get_FramePr();
			for (var Pos = StartPos + 1; Pos < EndPos; Pos++)
			{
				var TempElement = this.Content[Pos];

				if (type_Paragraph !== TempElement.GetType() || undefined === TempElement.Get_FramePr() || true != FramePr.Compare(TempElement.Get_FramePr()))
					return;
			}

			// Раз дошли до сюда, значит можно у всех выделенных параграфов менять настройку рамки
			var FrameParas = this.Content[StartPos].Internal_Get_FrameParagraphs();
			var FrameCount = FrameParas.length;
			for (var Pos = 0; Pos < FrameCount; Pos++)
			{
				FrameParas[Pos].Set_FramePr(FramePr, bDelete);
			}
		}
		else
		{
			var Element = this.Content[this.CurPos.ContentPos];

			if (type_Paragraph !== Element.GetType())
				return;

			// Возможно, предыдущий элемент является буквицей
			if (undefined === Element.Get_FramePr())
			{
				var PrevElement = Element.Get_DocumentPrev();

				if (type_Paragraph !== PrevElement.GetType() || undefined === PrevElement.Get_FramePr() || undefined === PrevElement.Get_FramePr().DropCap)
					return;

				Element = PrevElement;
			}

			var FrameParas = Element.Internal_Get_FrameParagraphs();
			var FrameCount = FrameParas.length;
			for (var Pos = 0; Pos < FrameCount; Pos++)
			{
				FrameParas[Pos].Set_FramePr(FramePr, bDelete);
			}
		}
	}
};
CDocumentContent.prototype.Add_ToContent = function(Pos, Item)
{
    this.Internal_Content_Add(Pos, Item);
};
CDocumentContent.prototype.Remove_FromContent = function(Pos, Count)
{
    this.Internal_Content_Remove(Pos, Count);
};
CDocumentContent.prototype.Concat_Paragraphs = function(Pos)
{
    if (Pos < this.Content.length - 1 && type_Paragraph === this.Content[Pos].Get_Type() && type_Paragraph === this.Content[Pos + 1].Get_Type())
    {
        var Para1 = this.Content[Pos];
        var Para2 = this.Content[Pos + 1];

        var OldSelectionStartPos = this.Selection.StartPos;
        var OldSelectionEndPos   = this.Selection.EndPos;
        var OldCurPos            = this.CurPos.ContentPos;

        Para1.Concat(Para2);
        this.Remove_FromContent(Pos + 1, 1);

        if (OldCurPos > Pos)
            this.CurPos.ContentPos = OldCurPos - 1;

        if (OldSelectionStartPos > Pos)
            this.Selection.StartPos = OldSelectionStartPos - 1;

        if (OldSelectionEndPos > Pos)
            this.Selection.EndPos = OldSelectionEndPos - 1;
    }
};
CDocumentContent.prototype.Get_ElementsCount = function()
{
    return this.Content.length;
};
CDocumentContent.prototype.Get_ElementByIndex = function(Index)
{
    return this.Content[Index];
};
CDocumentContent.prototype.GetContentPosition = function(bSelection, bStart, PosArray)
{
    if (undefined === PosArray)
        PosArray = [];

    var Pos = (true === bSelection ? (true === bStart ? this.Selection.StartPos : this.Selection.EndPos) : this.CurPos.ContentPos);
    PosArray.push({Class : this, Position : Pos});

    if (undefined !== this.Content[Pos] && this.Content[Pos].GetContentPosition)
        this.Content[Pos].GetContentPosition(bSelection, bStart, PosArray);

    return PosArray;
};
CDocumentContent.prototype.GetDocumentPositionFromObject = function(PosArray)
{
    if (!PosArray)
        PosArray = [];

    if (this.Parent && this.Parent.GetDocumentPositionFromObject)
        this.Parent.GetDocumentPositionFromObject(PosArray);

    return PosArray;
};
CDocumentContent.prototype.SetContentSelection = function(StartDocPos, EndDocPos, Depth, StartFlag, EndFlag)
{
    if ((0 === StartFlag && (!StartDocPos[Depth] || this !== StartDocPos[Depth].Class)) || (0 === EndFlag && (!EndDocPos[Depth] || this !== EndDocPos[Depth].Class)))
        return;

    if (this.Content.length <= 0)
        return;

    var StartPos = 0, EndPos = 0;
    switch (StartFlag)
    {
        case 0 : StartPos = StartDocPos[Depth].Position; break;
        case 1 : StartPos = 0; break;
        case -1: StartPos = this.Content.length - 1; break;
    }

    switch (EndFlag)
    {
        case 0 : EndPos = EndDocPos[Depth].Position; break;
        case 1 : EndPos = 0; break;
        case -1: EndPos = this.Content.length - 1; break;
    }

    var _StartDocPos = StartDocPos, _StartFlag = StartFlag;
    if (null !== StartDocPos && true === StartDocPos[Depth].Deleted)
    {
        if (StartPos < this.Content.length)
        {
            _StartDocPos = null;
            _StartFlag = 1;
        }
        else if (StartPos > 0)
        {
            StartPos--;
            _StartDocPos = null;
            _StartFlag = -1;
        }
        else
        {
            // Такого не должно быть
            return;
        }
    }

    var _EndDocPos = EndDocPos, _EndFlag = EndFlag;
    if (null !== EndDocPos && true === EndDocPos[Depth].Deleted)
    {
        if (EndPos < this.Content.length)
        {
            _EndDocPos = null;
            _EndFlag = 1;
        }
        else if (EndPos > 0)
        {
            EndPos--;
            _EndDocPos = null;
            _EndFlag = -1;
        }
        else
        {
            // Такого не должно быть
            return;
        }
    }

    StartPos = Math.min(this.Content.length - 1, Math.max(0, StartPos));
    EndPos   = Math.min(this.Content.length - 1, Math.max(0, EndPos));

    this.Selection.Use      = true;
    this.Selection.StartPos = StartPos;
    this.Selection.EndPos   = EndPos;

    if (StartPos !== EndPos)
    {
        this.Content[StartPos].SetContentSelection(_StartDocPos, null, Depth + 1, _StartFlag, StartPos > EndPos ? 1 : -1);
        this.Content[EndPos].SetContentSelection(null, _EndDocPos, Depth + 1, StartPos > EndPos ? -1 : 1, _EndFlag);

        var _StartPos = StartPos;
        var _EndPos = EndPos;
        var Direction = 1;

        if (_StartPos > _EndPos)
        {
            _StartPos = EndPos;
            _EndPos = StartPos;
            Direction = -1;
        }

        for (var CurPos = _StartPos + 1; CurPos < _EndPos; CurPos++)
        {
            this.Content[CurPos].SelectAll(Direction);
        }
    }
    else
    {
        this.Content[StartPos].SetContentSelection(_StartDocPos, _EndDocPos, Depth + 1, _StartFlag, _EndFlag);
    }
};
CDocumentContent.prototype.SetContentPosition = function(DocPos, Depth, Flag)
{
    if (0 === Flag && (!DocPos[Depth] || this !== DocPos[Depth].Class))
        return;

    if (this.Content.length <= 0)
        return;

    var Pos = 0;
    switch (Flag)
    {
        case 0 : Pos = DocPos[Depth].Position; break;
        case 1 : Pos = 0; break;
        case -1: Pos = this.Content.length - 1; break;
    }

    var _DocPos = DocPos, _Flag = Flag;
    if (null !== DocPos && true === DocPos[Depth].Deleted)
    {
        if (Pos < this.Content.length)
        {
            _DocPos = null;
            _Flag = 1;
        }
        else if (Pos > 0)
        {
            Pos--;
            _DocPos = null;
            _Flag = -1;
        }
        else
        {
            // Такого не должно быть
            return;
        }
    }

    Pos = Math.min(this.Content.length - 1, Math.max(0, Pos));
    this.CurPos.ContentPos = Pos;
    this.Content[Pos].SetContentPosition(_DocPos, Depth + 1, _Flag);
};
CDocumentContent.prototype.private_GetElementPageIndex = function(ElementPos, PageIndex, ColumnIndex, ColumnsCount)
{
    var Element = this.Content[ElementPos];
    if (!Element)
        return 0;

    var StartPage   = Element.Get_StartPage_Relative();
    var StartColumn = Element.Get_StartColumn();

    return ColumnIndex - StartColumn + (PageIndex - StartPage) * ColumnsCount;
};
CDocumentContent.prototype.private_GetElementPageIndexByXY = function(ElementPos, X, Y, PageIndex)
{
    return this.private_GetElementPageIndex(ElementPos, PageIndex, 0, 1);
};
CDocumentContent.prototype.Get_TopDocumentContent = function()
{
    var TopDocument = null;
    if (this.Parent && this.Parent.Get_TopDocumentContent)
        TopDocument = this.Parent.Get_TopDocumentContent();

    if (null !== TopDocument && undefined !== TopDocument)
        return TopDocument;

    return this;
};
CDocumentContent.prototype.private_RecalculateNumbering = function(Elements)
{
    if (true === AscCommon.g_oIdCounter.m_bLoad || true === AscCommon.g_oIdCounter.m_bRead || true === this.bPresentation)
        return;

    for (var Index = 0, Count = Elements.length; Index < Count; ++Index)
    {
        var Element = Elements[Index];
        if (type_Paragraph === Element.Get_Type())
            History.Add_RecalcNumPr(Element.Numbering_Get());
        else if (type_Paragraph === Element.Get_Type())
        {
            var ParaArray = [];
            Element.GetAllParagraphs({All : true}, ParaArray);

            for (var ParaIndex = 0, ParasCount = ParaArray.length; ParaIndex < ParasCount; ++ParaIndex)
            {
                var Para = ParaArray[ParaIndex];
                History.Add_RecalcNumPr(Para.Numbering_Get());
            }
        }
    }
};
CDocumentContent.prototype.Set_ParaPropsForVerticalTextInCell = function(isVerticalText)
{
    for (var Pos = 0, Count = this.Content.length; Pos < Count; ++Pos)
    {
        var Element = this.Content[Pos];
        if (type_Paragraph === Element.Get_Type())
            Element.Set_ParaPropsForVerticalTextInCell(isVerticalText);
    }
};
CDocumentContent.prototype.Set_LogicDocument = function(oLogicDocument)
{
    this.LogicDocument   = oLogicDocument;
    this.Styles          = oLogicDocument.Get_Styles();
    this.Numbering       = oLogicDocument.Get_Numbering();
    this.DrawingObjects  = oLogicDocument.DrawingObjects;
};
CDocumentContent.prototype.Get_LogicDocument = function()
{
	return this.LogicDocument;
};
CDocumentContent.prototype.RemoveTextSelection = function()
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
	{
		this.DrawingObjects.removeTextSelection();
	}
	else
	{
		this.RemoveSelection();
	}
};
CDocumentContent.prototype.CanUpdateTarget = function(CurPage)
{
	if (this.Pages.length <= 0)
		return false;

	if (this.Pages.length <= CurPage)
		return true;

	var nPos = (this.Selection.Use ? this.Selection.EndPos : this.CurPos.ContentPos);


	if (this.Pages[CurPage].EndPos > nPos)
		return true;
	else if (this.Pages[CurPage].EndPos < nPos)
		return false;

	var nElementPageIndex = this.private_GetElementPageIndex(nPos, CurPage, 0, 1);
	return this.Content[nPos].CanUpdateTarget(nElementPageIndex);
};
CDocumentContent.prototype.IsStartFromNewPage = function()
{
	if (this.Content.length <= 0)
		return false;

	return this.Content[0].IsStartFromNewPage();
};
CDocumentContent.prototype.PreDelete = function()
{
	for (var nIndex = 0, nCount = this.Content.length; nIndex < nCount; ++nIndex)
	{
		this.Content[nIndex].PreDelete();
	}
};
CDocumentContent.prototype.IsBlockLevelSdtContent = function()
{
	return (this.Parent && this.Parent instanceof CBlockLevelSdt);
};
CDocumentContent.prototype.IsSelectedAll = function()
{
	if (true === this.Selection.Use
		&& ((0 === this.Selection.StartPos && this.Content.length - 1 === this.Selection.EndPos)
		|| (0 === this.Selection.EndPos && this.Content.length - 1 === this.Selection.StartPos))
		&& true === this.Content[0].IsSelectedAll()
		&& true === this.Content[this.Content.length - 1].IsSelectedAll())
		return true;

	return false;
};
CDocumentContent.prototype.AddContentControl = function(nContentControlType)
{
	if (docpostype_DrawingObjects === this.CurPos.Type)
		return this.DrawingObjects.AddContentControl(nContentControlType);
	else
		return this.private_AddContentControl(nContentControlType);
};
CDocumentContent.prototype.GetAllContentControls = function(arrContentControls)
{
	if (!arrContentControls)
		arrContentControls = [];

	for (var nIndex = 0, nCount = this.Content.length; nIndex < nCount; ++nIndex)
	{
		this.Content[nIndex].GetAllContentControls(arrContentControls);
	}

	return arrContentControls;
};
CDocumentContent.prototype.GetMargins = function()
{
	if (this.Parent.GetMargins)
		return this.Parent.GetMargins();

	return {
		Top    : new CTableMeasurement(tblwidth_Mm, 0),
		Left   : new CTableMeasurement(tblwidth_Mm, 0),
		Bottom : new CTableMeasurement(tblwidth_Mm, 0),
		Right  : new CTableMeasurement(tblwidth_Mm, 0)
	};
};


function CDocumentContentStartState(DocContent)
{
    this.Content = [];
    for(var i = 0; i < DocContent.Content.length; ++i)
    {
        this.Content.push(DocContent.Content[i]);
    }
}

function CDocumentRecalculateObject()
{
    this.StartPage = 0;
    
    this.Pages    = [];
    this.Content  = [];
    this.ClipInfo = [];
}

CDocumentRecalculateObject.prototype = 
{
    Save : function(Doc)
    {
        this.StartPage = Doc.StartPage;        
        this.Pages     = Doc.Pages;
        this.ClipInfo  = Doc.ClipInfo;

        var Content = Doc.Content;
        var Count = Content.length;
        for ( var Index = 0; Index < Count; Index++ )
        {
            this.Content[Index] = Content[Index].SaveRecalculateObject();
        }
    },
        
    Load : function(Doc)
    {
        Doc.StartPage = this.StartPage;
        Doc.Pages     = this.Pages;
        Doc.ClipInfo  = this.ClipInfo;
        
        var Count = Doc.Content.length;
        for ( var Index = 0; Index < Count; Index++ )
        {
            Doc.Content[Index].LoadRecalculateObject( this.Content[Index] );
        }
    },
    
    Get_SummaryHeight : function()
    {
        var Height = 0;
        var PagesCount = this.Pages.length;
        for ( var Page = 0; Page < PagesCount; Page++ )
        {
            var Bounds = this.Get_PageBounds( Page );
            Height += Bounds.Bottom - Bounds.Top;
        }

        return Height;
    },
    
    Get_PageBounds : function(PageNum)
    {
        if ( this.Pages.length <= 0 )
            return { Top : 0, Left : 0, Right : 0, Bottom : 0 };

        if ( PageNum < 0 || PageNum > this.Pages.length )
            return this.Pages[0].Bounds;

        var Bounds = this.Pages[PageNum].Bounds;        

        return Bounds;
    },
    
    Get_DrawingFlowPos : function(FlowPos)
    {
        var Count = this.Content.length;
        for ( var Index = 0; Index < Count; Index++ )
        {
            this.Content[Index].Get_DrawingFlowPos( FlowPos );
        }
    }
        
};

//--------------------------------------------------------export----------------------------------------------------
window['AscCommonWord'] = window['AscCommonWord'] || {};
window['AscCommonWord'].CDocumentContent = CDocumentContent;