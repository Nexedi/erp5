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

// TODO: Сейчас Paragraph.Recalculate_FastWholeParagraph работает только на добавлении текста, надо переделать
//       алгоритм определения изменений, чтобы данная функция работала и при других изменениях.

// Import
var c_oAscLineDrawingRule = AscCommon.c_oAscLineDrawingRule;
var align_Left = AscCommon.align_Left;
var hdrftr_Header = AscCommon.hdrftr_Header;
var hdrftr_Footer = AscCommon.hdrftr_Footer;
var c_oAscFormatPainterState = AscCommon.c_oAscFormatPainterState;
var changestype_None = AscCommon.changestype_None;
var changestype_Paragraph_Content = AscCommon.changestype_Paragraph_Content;
var changestype_2_Element_and_Type = AscCommon.changestype_2_Element_and_Type;
var changestype_2_ElementsArray_and_Type = AscCommon.changestype_2_ElementsArray_and_Type;
var g_oTableId = AscCommon.g_oTableId;
var History = AscCommon.History;

var c_oAscHAnchor = Asc.c_oAscHAnchor;
var c_oAscXAlign = Asc.c_oAscXAlign;
var c_oAscYAlign = Asc.c_oAscYAlign;
var c_oAscVAnchor = Asc.c_oAscVAnchor;

var Page_Width     = 210;
var Page_Height    = 297;

var X_Left_Margin   = 30;  // 3   cm
var X_Right_Margin  = 15;  // 1.5 cm
var Y_Bottom_Margin = 20;  // 2   cm
var Y_Top_Margin    = 20;  // 2   cm

var X_Right_Field  = Page_Width  - X_Right_Margin;
var Y_Bottom_Field = Page_Height - Y_Bottom_Margin;

var docpostype_Content        = 0x00;
var docpostype_HdrFtr         = 0x02;
var docpostype_DrawingObjects = 0x03;
var docpostype_Footnotes      = 0x04;

var selectionflag_Common        = 0x000;
var selectionflag_Numbering     = 0x001;
var selectionflag_DrawingObject = 0x002;

var search_Common              = 0x0000; // Поиск в простом тексте
var search_Header              = 0x0100; // Поиск в верхнем колонтитуле
var search_Footer              = 0x0200; // Поиск в нижнем колонтитуле
var search_Footnote            = 0x0400; // Поиск в сноске

var search_HdrFtr_All          = 0x0001; // Поиск в колонтитуле, который находится на всех страницах
var search_HdrFtr_All_no_First = 0x0002; // Поиск в колонтитуле, который находится на всех страницах, кроме первой
var search_HdrFtr_First        = 0x0003; // Поиск в колонтитуле, который находится только на первой страниц
var search_HdrFtr_Even         = 0x0004; // Поиск в колонтитуле, который находится только на четных страницах
var search_HdrFtr_Odd          = 0x0005; // Поиск в колонтитуле, который находится только на нечетных страницах, включая первую
var search_HdrFtr_Odd_no_First = 0x0006; // Поиск в колонтитуле, который находится только на нечетных страницах, кроме первой

// Типы которые возвращают классы CParagraph и CTable после пересчета страницы
var recalcresult_NextElement = 0x01; // Пересчитываем следующий элемент
var recalcresult_PrevPage    = 0x02; // Пересчитываем заново предыдущую страницу
var recalcresult_CurPage     = 0x04; // Пересчитываем заново текущую страницу
var recalcresult_NextPage    = 0x08; // Пересчитываем следующую страницу
var recalcresult_NextLine    = 0x10; // Пересчитываем следующую строку
var recalcresult_CurLine     = 0x20; // Пересчитываем текущую строку
var recalcresult_CurPagePara = 0x40; // Специальный случай, когда мы встретили картинку в начале параграфа
var recalcresult_PrevLine    = 0x80; // Пересчитываем заново предыдущую строку (мб даже раньше, это должно идти в PRSW)

var recalcresultflags_Column            = 0x010000; // Пересчитываем только колонку
var recalcresultflags_Page              = 0x020000; // Пересчитываем всю страницу
var recalcresultflags_LastFromNewPage   = 0x040000; // Используется совсместно с recalcresult_NextPage, означает, что начало последнего элемента нужно перенести на новую страницу
var recalcresultflags_LastFromNewColumn = 0x080000; // Используется совсместно с recalcresult_NextPage, означает, что начало последнего элемента нужно перенести на новую колонку
var recalcresultflags_Footnotes         = 0x010000; // Сообщаем, что необходимо пересчитать сноски на данной странице

// Типы которые возвращают классы CDocument и CDocumentContent после пересчета страницы
var recalcresult2_End      = 0x00; // Документ рассчитан до конца
var recalcresult2_NextPage = 0x01; // Рассчет нужно продолжить
var recalcresult2_CurPage  = 0x02; // Нужно заново пересчитать данную страницу

var document_EditingType_Common = 0x00; // Обычный режим редактирования
var document_EditingType_Review = 0x01; // Режим рецензирования

var keydownflags_PreventDefault  = 0x0001;
var keydownflags_PreventKeyPress = 0x0002;

var keydownresult_PreventNothing  = 0x0000;
var keydownresult_PreventDefault  = 0x0001;
var keydownresult_PreventKeyPress = 0x0002;
var keydownresult_PreventAll      = 0xFFFF;

var MEASUREMENT_MAX_MM_VALUE = 1000; // Маскимальное значение в мм, используемое в документе (MS Word) - 55,87 см, или 558,7 мм.

function CDocumentColumnProps()
{
    this.W     = 0;
    this.Space = 0;
}
CDocumentColumnProps.prototype.put_W = function(W)
{
    this.W = W;
};
CDocumentColumnProps.prototype.get_W = function()
{
    return this.W;
};
CDocumentColumnProps.prototype.put_Space = function(Space)
{
    this.Space = Space;
};
CDocumentColumnProps.prototype.get_Space = function()
{
    return this.Space;
};

function CDocumentColumnsProps()
{
    this.EqualWidth = true;
    this.Num        = 1;
    this.Sep        = false;
    this.Space      = 30;

    this.Cols       = [];

    this.TotalWidth = 230;
}
CDocumentColumnsProps.prototype.From_SectPr = function(SectPr)
{
    var Columns = SectPr.Columns;

    this.TotalWidth = SectPr.Get_PageWidth() - SectPr.Get_PageMargin_Left() - SectPr.Get_PageMargin_Right();
    this.EqualWidth = Columns.EqualWidth;
    this.Num        = Columns.Num;
    this.Sep        = Columns.Sep;
    this.Space      = Columns.Space;

    for (var Index = 0, Count = Columns.Cols.length; Index < Count; ++Index)
    {
        var Col = new CDocumentColumnProps();
        Col.put_W(Columns.Cols[Index].W);
        Col.put_Space(Columns.Cols[Index].Space);
        this.Cols[Index] = Col;
    }
};
CDocumentColumnsProps.prototype.get_EqualWidth = function()
{
    return this.EqualWidth;
};
CDocumentColumnsProps.prototype.put_EqualWidth = function(EqualWidth)
{
    this.EqualWidth = EqualWidth;
};
CDocumentColumnsProps.prototype.get_Num = function()
{
    return this.Num;
};
CDocumentColumnsProps.prototype.put_Num = function(Num)
{
    this.Num = Num;
};
CDocumentColumnsProps.prototype.get_Sep = function()
{
    return this.Sep;
};
CDocumentColumnsProps.prototype.put_Sep = function(Sep)
{
    this.Sep = Sep;
};
CDocumentColumnsProps.prototype.get_Space = function()
{
    return this.Space;
};
CDocumentColumnsProps.prototype.put_Space = function(Space)
{
    this.Space = Space;
};
CDocumentColumnsProps.prototype.get_ColsCount = function()
{
    return this.Cols.length;
};
CDocumentColumnsProps.prototype.get_Col = function(Index)
{
    return this.Cols[Index];
};
CDocumentColumnsProps.prototype.put_Col = function(Index, Col)
{
    this.Cols[Index] = Col;
};
CDocumentColumnsProps.prototype.put_ColByValue = function(Index, W, Space)
{
    var Col = new CDocumentColumnProps();
    Col.put_W(W);
    Col.put_Space(Space);
    this.Cols[Index] = Col;
};
CDocumentColumnsProps.prototype.get_TotalWidth = function()
{
    return this.TotalWidth;
};

function CDocumentSectionProps(SectPr)
{
    if (SectPr)
    {
        this.W      = SectPr.Get_PageWidth();
        this.H      = SectPr.Get_PageHeight();
        this.Orient = SectPr.Get_Orientation();

        this.Left   = SectPr.Get_PageMargin_Left();
        this.Top    = SectPr.Get_PageMargin_Top();
        this.Right  = SectPr.Get_PageMargin_Right();
        this.Bottom = SectPr.Get_PageMargin_Bottom();

        this.Header = SectPr.Get_PageMargins_Header();
        this.Footer = SectPr.Get_PageMargins_Footer();
    }
    else
    {
        this.W      = undefined;
        this.H      = undefined;
        this.Orient = undefined;

        this.Left   = undefined;
        this.Top    = undefined;
        this.Right  = undefined;
        this.Bottom = undefined;

        this.Header = undefined;
        this.Footer = undefined;
    }
}
CDocumentSectionProps.prototype.get_W = function()
{
    return this.W;
};
CDocumentSectionProps.prototype.put_W = function(W)
{
    this.W = W;
};
CDocumentSectionProps.prototype.get_H = function()
{
    return this.H;
};
CDocumentSectionProps.prototype.put_H = function(H)
{
    this.H = H;
};
CDocumentSectionProps.prototype.get_Orientation = function()
{
    return this.Orient;
};
CDocumentSectionProps.prototype.put_Orientation = function(Orient)
{
    this.Orient = Orient;
};
CDocumentSectionProps.prototype.get_LeftMargin = function()
{
    return this.Left;
};
CDocumentSectionProps.prototype.put_LeftMargin = function(Left)
{
    this.Left = Left;
};
CDocumentSectionProps.prototype.get_TopMargin = function()
{
    return this.Top;
};
CDocumentSectionProps.prototype.put_TopMargin = function(Top)
{
    this.Top = Top;
};
CDocumentSectionProps.prototype.get_RightMargin = function()
{
    return this.Right;
};
CDocumentSectionProps.prototype.put_RightMargin = function(Right)
{
    this.Right = Right;
};
CDocumentSectionProps.prototype.get_BottomMargin = function()
{
    return this.Bottom;
};
CDocumentSectionProps.prototype.put_BottomMargin = function(Bottom)
{
    this.Bottom = Bottom;
};
CDocumentSectionProps.prototype.get_HeaderDistance = function()
{
    return this.Header;
};
CDocumentSectionProps.prototype.put_HeaderDistance = function(Header)
{
    this.Header = Header;
};
CDocumentSectionProps.prototype.get_FooterDistance = function()
{
    return this.Footer;
};
CDocumentSectionProps.prototype.put_FooterDistance = function(Footer)
{
    this.Footer = Footer;
};

function CSelectedElement(Element, SelectedAll)
{
    this.Element     = Element;
    this.SelectedAll = SelectedAll;
}

function CSelectedContent()
{
    this.Elements = [];

    this.DrawingObjects = [];
    this.Comments       = [];
    this.Maths          = [];

    this.HaveShape        = false;
    this.MoveDrawing      = false; // Только для переноса автофигур
    this.HaveMath         = false;
    this.CanConvertToMath = false;
}

CSelectedContent.prototype =
{
    Reset : function()
    {
        this.Elements = [];

        this.DrawingObjects = [];
        this.Comments       = [];
        this.Maths          = [];

        this.HaveShape   = false;
        this.MoveDrawing = false; // Только для переноса автофигур
        this.HaveMath    = false;
    },

    Add : function(Element)
    {
        this.Elements.push( Element );
    },

    Set_MoveDrawing : function(Value)
    {
        this.MoveDrawing = Value;
    },

    On_EndCollectElements : function(LogicDocument, bFromCopy)
    {
        // Теперь пройдемся по всем найденным элементам и выясним есть ли автофигуры и комментарии
        var Count = this.Elements.length;

        for (var Pos = 0; Pos < Count; Pos++)
        {
            var Element = this.Elements[Pos].Element;
            Element.GetAllDrawingObjects(this.DrawingObjects);
            Element.GetAllComments(this.Comments);
            Element.GetAllMaths(this.Maths);

            if (type_Paragraph === Element.Get_Type() && Count > 1)
                Element.Correct_Content();
        }

        this.HaveMath = (this.Maths.length > 0 ? true : false);

        // Проверка возможности конвертации имеющегося контента в контент для вставки в формулу.
        // Если формулы уже имеются, то ничего не конвертируем.
        if(!this.HaveMath)
        {
            if(1 === Count)
            {
                Element = this.Elements[0];
                if(type_Paragraph === Element.Element.GetType() && !Element.Element.Is_Empty({SkipEnd : true, SkipAnchor : true, SkipNewLine: true, SkipPlcHldr: true}) && !Element.SelectedAll )
                {
                    this.CanConvertToMath = true;
                }
            }
        }

        // Относительно картинок нас интересует только наличие автофигур с текстом.
        Count = this.DrawingObjects.length;
        for (var Pos = 0; Pos < Count; Pos++)
        {
            var DrawingObj = this.DrawingObjects[Pos];
            var ShapeType = DrawingObj.GraphicObj.getObjectType();

            if ( AscDFH.historyitem_type_Shape === ShapeType || AscDFH.historyitem_type_GroupShape === ShapeType )
            {
                this.HaveShape = true;
                break;
            }
        }

        // Если у комментария присутствует только начало или конец, тогда такой комментарий мы удяляем отсюда
        var Comments = {};
        Count = this.Comments.length;
        for (var Pos = 0; Pos < Count; Pos++)
        {
            var Element = this.Comments[Pos];

            var Id = Element.Comment.CommentId;
            if ( undefined === Comments[Id] )
                Comments[Id] = {};

            if ( true === Element.Comment.Start )
                Comments[Id].Start = Element.Paragraph;
            else
                Comments[Id].End   = Element.Paragraph;
        }

        // Пробегаемся по найденным комментариям и удаляем те, у которых нет начала или конца
        var NewComments = [];
        for (var Id in Comments)
        {
            var Element = Comments[Id];

            var Para = null;
            if ( undefined === Element.Start && undefined !== Element.End )
                Para = Element.End;
            else if ( undefined !== Element.Start && undefined === Element.End )
                Para = Element.Start;
            else if ( undefined !== Element.Start && undefined !== Element.End )
                NewComments.push(Id);

            if (null !== Para)
            {
                var OldVal = Para.DeleteCommentOnRemove;
                Para.DeleteCommentOnRemove = false;
                Para.RemoveCommentMarks(Id);
                Para.DeleteCommentOnRemove = OldVal;
            }
        }

        if (true !== bFromCopy)
        {
            // Новые комментарии мы дублируем и добавляем в список комментариев
            Count = NewComments.length;
            var Count2 = this.Comments.length;
            var DocumentComments = LogicDocument.Comments;
            for (var Pos = 0; Pos < Count; Pos++)
            {
                var Id = NewComments[Pos];
                var OldComment = DocumentComments.Get_ById(Id);

                if (null !== OldComment)
                {
                    var NewComment = OldComment.Copy();

                    if (History.Is_On())
                    {
                        DocumentComments.Add(NewComment);
                        editor.sync_AddComment(NewComment.Get_Id(), NewComment.Data);

                        // поправим Id в самих элементах ParaComment
                        for (var Pos2 = 0; Pos2 < Count2; Pos2++)
                        {
                            var Element = this.Comments[Pos2].Comment;
                            if (Id === Element.CommentId)
                            {
                                Element.Set_CommentId(NewComment.Get_Id());
                            }
                        }
                    }
                }
            }
        }
    },

    /**
     * Converts current content to ParaMath if it possible. Doesn't change current SelectedContent.
     * @returns {?AscCommonWord.ParaMath}
     * */
    ConvertToMath : function()
    {
        if(!this.CanConvertToMath)
        {
            return null;
        }

        var oParagraph = this.Elements[0].Element;
        var aContent = oParagraph.Content, aRunContent;
        var oParaMath = new AscCommonWord.ParaMath();
        oParaMath.Root.Load_FromMenu(c_oAscMathType.Default_Text, oParagraph);
        oParaMath.Root.Correct_Content(true);
        for(var i = 0; i < aContent.length; ++i)
        {
            if(aContent[i].Get_Type() === para_Run)
            {
                aRunContent = aContent[i].Content;
                for(var j = 0; j < aRunContent.length; ++j)
                {
                    oParaMath.Add(aRunContent[j]);
                }
            }
        }
        return oParaMath;
    }
};

function CDocumentRecalculateState()
{
    this.Id           = null;

    this.PageIndex    = 0;
    this.SectionIndex = 0;
    this.ColumnIndex  = 0;
    this.Start        = true;
    this.StartIndex   = 0;
    this.StartPage    = 0;

    this.ResetStartElement = false;
    this.MainStartPos      = -1;
}

function CDocumentRecalculateHdrFtrPageCountState()
{
	this.Id        = null;
	this.PageIndex = 0;
	this.PageCount = -1;
}

function Document_Recalculate_Page()
{
    var LogicDocument = editor.WordControl.m_oLogicDocument;
    LogicDocument.Recalculate_Page();
}

function Document_Recalculate_HdrFtrPageCount()
{
	var LogicDocument = editor.WordControl.m_oLogicDocument;
	LogicDocument.private_RecalculateHdrFtrPageCountUpdate();
}

function CDocumentPageSection()
{
    this.Pos    = 0;
    this.EndPos = -1;

    this.Y      = 0;
    this.YLimit = 0;

    this.YLimit2 = 0;

    this.Columns = [];
    this.ColumnsSep = false;

    this.IterationsCount          = 0;
    this.CurrentY                 = 0;
    this.CanRecalculateBottomLine = true;
}
CDocumentPageSection.prototype.Copy = function()
{
    var NewSection = new CDocumentPageSection();

    NewSection.Pos    = this.Pos;
    NewSection.EndPos = this.EndPos;
    NewSection.Y      = this.Y;
    NewSection.YLimit = this.YLimit;

    for (var ColumnIndex = 0, Count = this.Columns.length; ColumnIndex < Count; ++ColumnIndex)
    {
		NewSection.Columns[ColumnIndex] = this.Columns[ColumnIndex].Copy();
    }

    return NewSection;
};
CDocumentPageSection.prototype.Shift = function(Dx, Dy)
{
    this.Y      += Dy;
    this.YLimit += Dy;

    for (var ColumnIndex = 0, Count = this.Columns.length; ColumnIndex < Count; ++ColumnIndex)
    {
        this.Columns[ColumnIndex].Shift(Dx, Dy);
    }
};
CDocumentPageSection.prototype.Is_CalculatingSectionBottomLine = function()
{
    if (this.IterationsCount > 0 && true === this.CanRecalculateBottomLine)
        return true;

    return false;
};
CDocumentPageSection.prototype.Can_RecalculateBottomLine = function()
{
    return this.CanRecalculateBottomLine;
};
CDocumentPageSection.prototype.Get_Y = function()
{
    return this.Y;
};
CDocumentPageSection.prototype.Get_YLimit = function()
{
    if (0 === this.IterationsCount)
        return this.YLimit;
    else
        return this.CurrentY;
};
CDocumentPageSection.prototype.Calculate_BottomLine = function(isIncrease)
{
    if (0 === this.IterationsCount)
    {
        var SumHeight = 0;
        for (var ColumnIndex = 0, ColumnsCount = this.Columns.length; ColumnIndex < ColumnsCount; ++ColumnIndex)
        {
            if (true !== this.Columns[ColumnIndex].Empty)
            {
                SumHeight += this.Columns[ColumnIndex].Bounds.Bottom - this.Y;
            }
        }

        this.CurrentY = this.Y + SumHeight / ColumnsCount;
    }
    else
    {
        if (false === isIncrease)
            this.CurrentY -= 5;
        else
            this.CurrentY += 5;
    }

    this.CurrentY = Math.min(this.CurrentY, this.YLimit2);

    this.IterationsCount++;
    return this.CurrentY;
};
CDocumentPageSection.prototype.Reset_Columns = function()
{
    for (var ColumnIndex = 0, Count = this.Columns.length; ColumnIndex < Count; ++ColumnIndex)
    {
        this.Columns[ColumnIndex].Reset();
    }
};
CDocumentPageSection.prototype.DoNotRecalc_BottomLine = function()
{
    this.CanRecalculateBottomLine = false;
};

function CDocumentPageColumn()
{
    this.Bounds = new CDocumentBounds(0, 0, 0, 0);
    this.Pos    = 0;
    this.EndPos = -1;
    this.Empty  = true;

    this.X      = 0;
    this.Y      = 0;
    this.XLimit = 0;
    this.YLimit = 0;

    this.SpaceBefore = 0;
    this.SpaceAfter  = 0;
}
CDocumentPageColumn.prototype.Copy = function()
{
    var NewColumn = new CDocumentPageColumn();

    NewColumn.Bounds.CopyFrom(this.Bounds);
    NewColumn.Pos    = this.Pos;
    NewColumn.EndPos = this.EndPos;
    NewColumn.X      = this.X;
    NewColumn.Y      = this.Y;
    NewColumn.XLimit = this.XLimit;
    NewColumn.YLimit = this.YLimit;

    return NewColumn;
};
CDocumentPageColumn.prototype.Shift = function(Dx, Dy)
{
    this.X      += Dx;
    this.XLimit += Dx;
    this.Y      += Dy;
    this.YLimit += Dy;

    this.Bounds.Shift(Dx, Dy);
};
CDocumentPageColumn.prototype.Reset = function()
{
    this.Bounds.Reset();
    this.Pos    = 0;
    this.EndPos = -1;
    this.Empty  = true;

    this.X      = 0;
    this.Y      = 0;
    this.XLimit = 0;
    this.YLimit = 0;
};
CDocumentPageColumn.prototype.IsEmpty = function()
{
	return this.Empty;
};

function CDocumentPage()
{
    this.Width   = 0;
    this.Height  = 0;
    this.Margins =
    {
        Left   : 0,
        Right  : 0,
        Top    : 0,
        Bottom : 0
    };

    this.Bounds = new CDocumentBounds(0,0,0,0);
    this.Pos    = 0;
    this.EndPos = -1;

    this.X      = 0;
    this.Y      = 0;
    this.XLimit = 0;
    this.YLimit = 0;

    this.Sections = [];

    this.EndSectionParas = [];

    this.ResetStartElement = false;
}

CDocumentPage.prototype.Update_Limits = function(Limits)
{
    this.X      = Limits.X;
    this.XLimit = Limits.XLimit;
    this.Y      = Limits.Y;
    this.YLimit = Limits.YLimit;
};
CDocumentPage.prototype.Shift = function(Dx, Dy)
{
    this.X      += Dx;
    this.XLimit += Dx;
    this.Y      += Dy;
    this.YLimit += Dy;

    this.Bounds.Shift(Dx, Dy);

    for (var SectionIndex = 0, Count = this.Sections.length; SectionIndex < Count; ++SectionIndex)
    {
        this.Sections[SectionIndex].Shift(Dx, Dy);
    }
};
CDocumentPage.prototype.Check_EndSectionPara = function(Element)
{
    var Count = this.EndSectionParas.length;
    for ( var Index = 0; Index < Count; Index++ )
    {
        if ( Element === this.EndSectionParas[Index] )
            return true;
    }

    return false;
};
CDocumentPage.prototype.Copy = function()
{
    var NewPage = new CDocumentPage();

    NewPage.Width          = this.Width;
    NewPage.Height         = this.Height;
    NewPage.Margins.Left   = this.Margins.Left;
    NewPage.Margins.Right  = this.Margins.Right;
    NewPage.Margins.Top    = this.Margins.Top;
    NewPage.Margins.Bottom = this.Margins.Bottom;

    NewPage.Bounds.CopyFrom(this.Bounds);
    NewPage.Pos    = this.Pos;
    NewPage.EndPos = this.EndPos;
    NewPage.X      = this.X;
    NewPage.Y      = this.Y;
    NewPage.XLimit = this.XLimit;
    NewPage.YLimit = this.YLimit;

    for (var SectionIndex = 0, Count = this.Sections.length; SectionIndex < Count; ++SectionIndex)
    {
        NewPage.Sections[SectionIndex] = this.Sections[SectionIndex].Copy();
    }

    return NewPage;
};

function CStatistics(LogicDocument)
{
    this.LogicDocument = LogicDocument;
    this.Api           = LogicDocument.Get_Api();

    this.Id       = null; // Id таймера для подсчета всего кроме страниц
    this.PagesId  = null; // Id таймера для подсчета страниц

    this.StartPos = 0;

    this.Pages           = 0;
    this.Words           = 0;
    this.Paragraphs      = 0;
    this.SymbolsWOSpaces = 0;
    this.SymbolsWhSpaces = 0;
}

CStatistics.prototype =
{
//-----------------------------------------------------------------------------------
// Функции для запуска и остановки сбора статистики
//-----------------------------------------------------------------------------------
    Start : function()
    {
        this.StartPos = 0;
        this.CurPage  = 0;

        this.Pages           = 0;
        this.Words           = 0;
        this.Paragraphs      = 0;
        this.SymbolsWOSpaces = 0;
        this.SymbolsWhSpaces = 0;


        var LogicDocument = this.LogicDocument;
        this.PagesId = setTimeout(function(){LogicDocument.Statistics_GetPagesInfo();}, 1);
        this.Id      = setTimeout(function(){LogicDocument.Statistics_GetParagraphsInfo();}, 1);
        this.Send();
    },

    Next_ParagraphsInfo : function(StartPos)
    {
        this.StartPos = StartPos;
        var LogicDocument = this.LogicDocument;
        clearTimeout(this.Id);
        this.Id = setTimeout(function(){LogicDocument.Statistics_GetParagraphsInfo();}, 1);
        this.Send();
    },

    Next_PagesInfo : function()
    {
        var LogicDocument = this.LogicDocument;
        clearTimeout(this.PagesId);
        this.PagesId = setTimeout(function(){LogicDocument.Statistics_GetPagesInfo();}, 100);
        this.Send();
    },

    Stop_PagesInfo : function()
    {
        if (null !== this.PagesId)
        {
            clearTimeout(this.PagesId);
            this.PagesId = null;
        }

        this.Check_Stop();
    },

    Stop_ParagraphsInfo : function()
    {
        if (null != this.Id)
        {
            clearTimeout(this.Id);
            this.Id = null;
        }

        this.Check_Stop();
    },

    Check_Stop : function()
    {
        if (null === this.Id && null === this.PagesId)
        {
            this.Send();
            this.Api.sync_GetDocInfoEndCallback();
        }
    },

    Send : function()
    {
        var Stats =
        {
            PageCount      : this.Pages,
            WordsCount     : this.Words,
            ParagraphCount : this.Paragraphs,
            SymbolsCount   : this.SymbolsWOSpaces,
            SymbolsWSCount : this.SymbolsWhSpaces
        };

        this.Api.sync_DocInfoCallback(Stats);
    },
//-----------------------------------------------------------------------------------
// Функции для пополнения статистики
//-----------------------------------------------------------------------------------
    Add_Paragraph : function (Count)
    {
        if ( "undefined" != typeof( Count ) )
            this.Paragraphs += Count;
        else
            this.Paragraphs++;
    },

    Add_Word : function(Count)
    {
        if ( "undefined" != typeof( Count ) )
            this.Words += Count;
        else
            this.Words++;
    },

    Update_Pages : function(PagesCount)
    {
        this.Pages = PagesCount;
    },

    Add_Symbol : function(bSpace)
    {
        this.SymbolsWhSpaces++;
        if ( true != bSpace )
            this.SymbolsWOSpaces++;
    }
};

function CDocumentRecalcInfo()
{
    this.FlowObject                = null;   // Текущий float-объект, который мы пересчитываем
    this.FlowObjectPageBreakBefore = false;  // Нужно ли перед float-объектом поставить pagebreak
    this.FlowObjectPage            = 0;      // Количество обработанных страниц
    this.FlowObjectElementsCount   = 0;      // Количество элементов подряд идущих в рамке (только для рамок)
    this.RecalcResult              = recalcresult_NextElement;

    this.WidowControlParagraph     = null;   // Параграф, который мы пересчитываем из-за висячих строк
    this.WidowControlLine          = -1;     // Номер строки, перед которой надо поставить разрыв страницы
    this.WidowControlReset         = false;  //

    this.KeepNextParagraph         = null;    // Параграф, который надо пересчитать из-за того, что следующий начался с новой страницы
    this.KeepNextEndParagraph      = null;    // Параграф, на котором определилось, что нужно делать пересчет предыдущих

    this.FrameRecalc               = false;   // Пересчитываем ли рамку
    this.ParaMath                  = null;

    this.FootnoteReference         = null;    // Ссылка на сноску, которую мы пересчитываем
    this.FootnotePage              = 0;
    this.FootnoteColumn            = 0;

    this.AdditionalInfo            = null;

    this.NeedRecalculateFromStart  = false;
}

CDocumentRecalcInfo.prototype =
{
    Reset : function()
    {
        this.FlowObject                = null;
        this.FlowObjectPageBreakBefore = false;
        this.FlowObjectPage            = 0;
        this.FlowObjectElementsCount   = 0;
        this.RecalcResult              = recalcresult_NextElement;

        this.WidowControlParagraph     = null;
        this.WidowControlLine          = -1;
        this.WidowControlReset         = false;

        this.KeepNextParagraph         = null;
        this.KeepNextEndParagraph      = null;

        this.ParaMath                  = null;

        this.FootnoteReference         = null;
        this.FootnotePage              = 0;
        this.FootnoteColumn            = 0;
    },

    Can_RecalcObject : function()
    {
        if (null === this.FlowObject && null === this.WidowControlParagraph && null === this.KeepNextParagraph && null == this.ParaMath && null === this.FootnoteReference)
            return true;

        return false;
    },

    Can_RecalcWidowControl : function()
    {
        // TODO: Пока нельзя отдельно проверять объекты, вызывающие пересчет страниц, потому что возможны зависания.
        //       Надо обдумать новую более грамотную схему, при которой можно будет вызывать независимые пересчеты заново.
        return this.Can_RecalcObject();
    },

    Set_FlowObject : function(Object, RelPage, RecalcResult, ElementsCount, AdditionalInfo)
    {
        this.FlowObject              = Object;
        this.FlowObjectPage          = RelPage;
        this.FlowObjectElementsCount = ElementsCount;
        this.RecalcResult            = RecalcResult;
        this.AdditionalInfo          = AdditionalInfo;
    },

    Set_ParaMath : function(Object)
    {
        this.ParaMath = Object;
    },

    Check_ParaMath: function(ParaMath)
    {
        if ( ParaMath === this.ParaMath )
            return true;

        return false;
    },

    Check_FlowObject : function(FlowObject)
    {
        if ( FlowObject === this.FlowObject )
            return true;

        return false;
    },

    Set_PageBreakBefore : function(Value)
    {
        this.FlowObjectPageBreakBefore = Value;
    },

    Is_PageBreakBefore : function()
    {
        return this.FlowObjectPageBreakBefore;
    },

    Set_KeepNext : function(Paragraph, EndParagraph)
    {
        this.KeepNextParagraph    = Paragraph;
        this.KeepNextEndParagraph = EndParagraph;
    },

    Check_KeepNext : function(Paragraph)
    {
        if ( Paragraph === this.KeepNextParagraph )
            return true;

        return false;
    },

    Check_KeepNextEnd : function(Paragraph)
    {
        if (Paragraph === this.KeepNextEndParagraph)
            return true;

        return false;
    },

    Need_ResetWidowControl : function()
    {
        this.WidowControlReset = true;
    },

    Reset_WidowControl : function()
    {
        if (true === this.WidowControlReset)
        {
            this.WidowControlParagraph = null;
            this.WidowControlLine      = -1;
            this.WidowControlReset     = false;
        }
    },

    Set_WidowControl : function(Paragraph, Line)
    {
        this.WidowControlParagraph = Paragraph;
        this.WidowControlLine      = Line;
    },

    Check_WidowControl : function(Paragraph, Line)
    {
        if (Paragraph === this.WidowControlParagraph && Line === this.WidowControlLine)
            return true;

        return false;
    },

    Set_FrameRecalc  : function(Value)
    {
        this.FrameRecalc = Value;
    },

    Set_FootnoteReference : function(oFootnoteReference, nPageAbs, nColumnAbs)
    {
        this.FootnoteReference = oFootnoteReference;
        this.FootnotePage      = nPageAbs;
		this.FootnoteColumn    = nColumnAbs;
    },

    Check_FootnoteReference : function(oFootnoteReference)
    {
        return (this.FootnoteReference === oFootnoteReference ? true : false);
    },

    Reset_FootnoteReference : function()
    {
        this.FootnoteReference         = null;
		this.FootnotePage              = 0;
		this.FootnoteColumn            = 0;
		this.FlowObjectPageBreakBefore = false;
    },

	Set_NeedRecalculateFromStart : function(isNeedRecalculate)
	{
		this.NeedRecalculateFromStart = isNeedRecalculate;
	},

	Is_NeedRecalculateFromStart : function()
	{
		return this.NeedRecalculateFromStart;
	}

};

function CDocumentFieldsManager()
{
	this.m_aFields = [];

	this.m_oMailMergeFields = {};

	this.m_aComplexFields = [];
}

CDocumentFieldsManager.prototype.Register_Field = function(oField)
{
    this.m_aFields.push(oField);

    var nFieldType = oField.Get_FieldType();
    if (fieldtype_MERGEFIELD === nFieldType)
    {
        var sName = oField.Get_Argument(0);
        if (undefined !== sName)
        {
            if (undefined === this.m_oMailMergeFields[sName])
                this.m_oMailMergeFields[sName] = [];

            this.m_oMailMergeFields[sName].push(oField);
        }
    }
};
CDocumentFieldsManager.prototype.Update_MailMergeFields = function(Map)
{
    for (var FieldName in this.m_oMailMergeFields)
    {
        for (var Index = 0, Count = this.m_oMailMergeFields[FieldName].length; Index < Count; Index++)
        {
            var oField = this.m_oMailMergeFields[FieldName][Index];
            oField.Map_MailMerge(Map[FieldName]);
        }
    }
};
CDocumentFieldsManager.prototype.Replace_MailMergeFields = function(Map)
{
    for (var FieldName in this.m_oMailMergeFields)
    {
        for (var Index = 0, Count = this.m_oMailMergeFields[FieldName].length; Index < Count; Index++)
        {
            var oField = this.m_oMailMergeFields[FieldName][Index];
            oField.Replace_MailMerge(Map[FieldName]);
        }
    }
};
CDocumentFieldsManager.prototype.Restore_MailMergeTemplate = function()
{
    if (true === AscCommon.CollaborativeEditing.Is_SingleUser())
    {
        // В такой ситуации мы восстанавливаем стандартный текст полей. Чтобы это сделать нам сначала надо пробежаться
        // по всем таким полям, определить параграфы, в которых необходимо восстановить поля. Залочить эти параграфы,
        // и произвести восстановление полей.

        var FieldsToRestore    = [];
        var FieldsRemain       = [];
        var ParagrapsToRestore = [];
        for (var FieldName in this.m_oMailMergeFields)
        {
            for (var Index = 0, Count = this.m_oMailMergeFields[FieldName].length; Index < Count; Index++)
            {
                var oField = this.m_oMailMergeFields[FieldName][Index];
                var oFieldPara = oField.GetParagraph();

                if (oFieldPara && oField.Is_NeedRestoreTemplate())
                {
                    var bNeedAddPara = true;
                    for (var ParaIndex = 0, ParasCount = ParagrapsToRestore.length; ParaIndex < ParasCount; ParaIndex++)
                    {
                        if (oFieldPara === ParagrapsToRestore[ParaIndex])
                        {
                            bNeedAddPara = false;
                            break;
                        }
                    }
                    if (true === bNeedAddPara)
                        ParagrapsToRestore.push(oFieldPara);

                    FieldsToRestore.push(oField);
                }
                else
                {
                    FieldsRemain.push(oField);
                }
            }
        }

        var LogicDocument = (ParagrapsToRestore.length > 0 ? ParagrapsToRestore[0].LogicDocument : null);
        if (LogicDocument && false === LogicDocument.Document_Is_SelectionLocked(changestype_None, { Type : changestype_2_ElementsArray_and_Type, Elements : ParagrapsToRestore, CheckType : changestype_Paragraph_Content }))
        {
            History.Create_NewPoint(AscDFH.historydescription_Document_RestoreFieldTemplateText);
            for (var nIndex = 0, nCount = FieldsToRestore.length; nIndex < nCount; nIndex++)
            {
                var oField = FieldsToRestore[nIndex];
                oField.Restore_StandardTemplate();
            }

            for (var nIndex = 0, nCount = FieldsRemain.length; nIndex < nCount; nIndex++)
            {
                var oField = FieldsRemain[nIndex];
                oField.Restore_Template();
            }
        }
        else
        {
            // Восстанавливать ничего не надо просто возващаем значения тимплейтов
            for (var FieldName in this.m_oMailMergeFields)
            {
                for (var Index = 0, Count = this.m_oMailMergeFields[FieldName].length; Index < Count; Index++)
                {
                    var oField = this.m_oMailMergeFields[FieldName][Index];
                    oField.Restore_Template();
                }
            }
        }
    }
    else
    {
        for (var FieldName in this.m_oMailMergeFields)
        {
            for (var Index = 0, Count = this.m_oMailMergeFields[FieldName].length; Index < Count; Index++)
            {
                var oField = this.m_oMailMergeFields[FieldName][Index];
                oField.Restore_Template();
            }
        }
    }
};
CDocumentFieldsManager.prototype.GetAllFieldsByType = function(nType)
{
	var arrFields = [];
	for (var nIndex = 0, nCount = this.m_aFields.length; nIndex < nCount; ++nIndex)
	{
		var oField = this.m_aFields[nIndex];
		if (nType === oField.Get_FieldType() && oField.Is_UseInDocument())
		{
			arrFields.push(oField);
		}
	}
	return arrFields;
};
CDocumentFieldsManager.prototype.RegisterComplexField = function(oComplexField)
{
	this.m_aComplexFields.push(oComplexField);
};

var selected_None              = -1;
var selected_DrawingObject     = 0;
var selected_DrawingObjectText = 1;

function CSelectedElementsInfo()
{
    this.m_bTable          = false; // Находится курсор или выделение целиком в какой-нибудь таблице
    this.m_bMixedSelection = false; // Попадает ли в выделение одновременно несколько элементов
    this.m_nDrawing        = selected_None;
    this.m_pParagraph      = null;  // Параграф, в котором находится выделение
    this.m_oMath           = null;  // Формула, в которой находится выделение
    this.m_oHyperlink      = null;  // Гиперссылка, в которой находится выделение
    this.m_oField          = null;  // Поле, в котором находится выделение
    this.m_oCell           = null;  // Выделенная ячейка (специальная ситуация, когда выделена ровно одна ячейка)
	this.m_oBlockLevelSdt  = null;  // Если мы находимся в классе CBlockLevelSdt
	this.m_oInlineLevelSdt = null;  // Если мы находимся в классе CInlineLevelSdt

    this.Reset = function()
    {
        this.m_bSelection      = false;
        this.m_bTable          = false;
        this.m_bMixedSelection = false;
        this.m_nDrawing        = -1;
    };

    this.Set_Math = function(Math)
    {
        this.m_oMath = Math;
    };

    this.Set_Field = function(Field)
    {
        this.m_oField = Field;
    };

    this.Set_Hyperlink = function(Hyperlink)
    {
        this.m_oHyperlink = Hyperlink;
    };

    this.Get_Math = function()
    {
        return this.m_oMath;
    };

    this.Get_Field = function()
    {
        return this.m_oField;
    };

    this.Get_Hyperlink = function()
    {
        return this.m_oHyperlink;
    };

    this.Set_Table = function()
    {
        this.m_bTable = true;
    };

    this.Set_Drawing = function(nDrawing)
    {
        this.m_nDrawing = nDrawing;
    };

    this.Is_DrawingObjSelected = function()
    {
        return ( this.m_nDrawing === selected_DrawingObject ? true : false );
    };

    this.Set_MixedSelection = function()
    {
        this.m_bMixedSelection = true;
    };

    this.Is_InTable = function()
    {
        return this.m_bTable;
    };

    this.Is_MixedSelection = function()
    {
        return this.m_bMixedSelection;
    };

    this.Set_SingleCell = function(Cell)
    {
        this.m_oCell = Cell;
    };

    this.Get_SingleCell = function()
    {
        return this.m_oCell;
    };
}
CSelectedElementsInfo.prototype.SetParagraph = function(Para)
{
	this.m_pParagraph = Para;
};
CSelectedElementsInfo.prototype.GetParagraph = function()
{
	return this.m_pParagraph;
};
CSelectedElementsInfo.prototype.SetBlockLevelSdt = function(oSdt)
{
	this.m_oBlockLevelSdt = oSdt;
};
CSelectedElementsInfo.prototype.GetBlockLevelSdt = function()
{
	return this.m_oBlockLevelSdt;
};
CSelectedElementsInfo.prototype.SetInlineLevelSdt = function(oSdt)
{
	this.m_oInlineLevelSdt = oSdt;
};
CSelectedElementsInfo.prototype.GetInlineLevelSdt = function()
{
	return this.m_oInlineLevelSdt;
};

var document_compatibility_mode_Word14 = 14;
var document_compatibility_mode_Word15 = 15;

function CDocumentSettings()
{
    this.MathSettings      = undefined !== CMathSettings ? new CMathSettings() : {};
    this.CompatibilityMode = document_compatibility_mode_Word14;
}

/**
 * Основной класс для работы с документом в Word.
 * @param DrawingDocument
 * @param isMainLogicDocument
 * @constructor
 * @extends {CDocumentContentBase}
 */
function CDocument(DrawingDocument, isMainLogicDocument)
{
	CDocumentContentBase.call(this);

    //------------------------------------------------------------------------------------------------------------------
    //  Сохраняем ссылки на глобальные объекты
    //------------------------------------------------------------------------------------------------------------------
    this.History              = History;
    this.IdCounter            = AscCommon.g_oIdCounter;
    this.TableId              = g_oTableId;
    this.CollaborativeEditing = (("undefined" !== typeof(AscCommon.CWordCollaborativeEditing) && AscCommon.CollaborativeEditing instanceof AscCommon.CWordCollaborativeEditing) ? AscCommon.CollaborativeEditing : null);
    this.Api                  = editor;
    //------------------------------------------------------------------------------------------------------------------
    //  Выставляем ссылки на главный класс
    //------------------------------------------------------------------------------------------------------------------
    if (false !== isMainLogicDocument)
    {
        if (this.History)
            this.History.Set_LogicDocument(this);

        if (this.CollaborativeEditing)
            this.CollaborativeEditing.m_oLogicDocument = this;
    }
    //__________________________________________________________________________________________________________________

    this.Id = this.IdCounter.Get_NewId();

    this.NumInfoCounter = 0;

    // Сначала настраиваем размеры страницы и поля
    this.SectPr = new CSectionPr(this);
    this.SectionsInfo = new CDocumentSectionsInfo();

    this.Content[0] = new Paragraph(DrawingDocument, this);
    this.Content[0].Set_DocumentNext(null);
    this.Content[0].Set_DocumentPrev(null);

    this.Settings = new CDocumentSettings();

    this.CurPos  =
    {
        X          : 0,
        Y          : 0,
        ContentPos : 0, // в зависимости, от параметра Type: позиция в Document.Content
        RealX      : 0, // позиция курсора, без учета расположения букв
        RealY      : 0, // это актуально для клавиш вверх и вниз
        Type       : docpostype_Content
    };

	this.Selection =
    {
        Start    : false,
        Use      : false,
        StartPos : 0,
        EndPos   : 0,
        Flag     : selectionflag_Common,
        Data     : null,
        UpdateOnRecalc : false,
		WordSelected : false,
        DragDrop : { Flag : 0, Data : null }  // 0 - не drag-n-drop, и мы его проверяем, 1 - drag-n-drop, -1 - не проверять drag-n-drop
    };

    if (false !== isMainLogicDocument)
        this.ColumnsMarkup = new CColumnsMarkup();

    // Здесь мы храним инфрмацию, связанную с разбивкой на страницы и самими страницами
    this.Pages = [];

    this.RecalcInfo = new CDocumentRecalcInfo();

    this.RecalcId     = 0; // Номер пересчета
    this.FullRecalc   = new CDocumentRecalculateState(); // Объект полного пересчета
    this.HdrFtrRecalc = new CDocumentRecalculateHdrFtrPageCountState(); // Объект дополнительного пересчета колонтитулов после полного пересчета

    this.TurnOffRecalc          = 0;
    this.TurnOffInterfaceEvents = false;
    this.TurnOffRecalcCurPos    = false;

    this.CheckEmptyElementsOnSelection = true; // При выделении проверять или нет пустой параграф в конце/начале выделения.

    this.Numbering = new CNumbering();
    this.Styles    = new CStyles();
    this.Styles.Set_LogicDocument(this);

    this.DrawingDocument = DrawingDocument;

    this.NeedUpdateTarget = false;

    // Флаг, который контролирует нужно ли обновлять наш курсор у остальных редакторов нашего документа.
    // Также следим за частотой обновления, чтобы оно проходило не чаще одного раза в секунду.
    this.NeedUpdateTargetForCollaboration = true;
    this.LastUpdateTargetTime             = 0;

    this.ReindexStartPos = 0;

    // Класс для работы с колонтитулами
    this.HdrFtr = new CHeaderFooterController(this, this.DrawingDocument);

    // Класс для работы с поиском
    this.SearchInfo =
    {
        Id       : null,
        StartPos : 0,
        CurPage  : 0,
        String   : null
    };

    // Позция каретки
    this.TargetPos =
    {
        X       : 0,
        Y       : 0,
        PageNum : 0
    };

    this.CopyTextPr = null; // TextPr для копирования по образцу
    this.CopyParaPr = null; // ParaPr для копирования по образцу

    // Класс для работы со статискикой документа
    this.Statistics = new CStatistics( this );

    this.HighlightColor = null;

    if(typeof CComments !== "undefined")
        this.Comments = new CComments();

    this.Lock = new AscCommon.CLock();

    this.m_oContentChanges = new AscCommon.CContentChanges(); // список изменений(добавление/удаление элементов)

    // Массив укзателей на все инлайновые графические объекты
    this.DrawingObjects = null;

    if (typeof CGraphicObjects !== "undefined")
        this.DrawingObjects = new CGraphicObjects(this, this.DrawingDocument, this.Api);

    this.theme          = AscFormat.GenerateDefaultTheme(this);
    this.clrSchemeMap   = AscFormat.GenerateDefaultColorMap();

    // Класс для работы с поиском и заменой в документе
    this.SearchEngine = null;
    if (typeof CDocumentSearch !== "undefined")
        this.SearchEngine = new CDocumentSearch();

    // Параграфы, в которых есть ошибки в орфографии (объект с ключом - Id параграфа)
    this.Spelling = new CDocumentSpelling();

    // Дополнительные настройки
    this.UseTextShd                = true;  // Использовать ли заливку текста
    this.ForceCopySectPr           = false; // Копировать ли настройки секции, если родительский класс параграфа не документ
    this.CopyNumberingMap          = null;  // Мап старый индекс -> новый индекс для копирования нумерации
    this.CheckLanguageOnTextAdd    = false; // Проверять ли язык при добавлении текста в ран
	this.RemoveCommentsOnPreDelete = false; // Удалять ли комментарий при удалением объекта

    // Мап для рассылки
    this.MailMergeMap             = null;
    this.MailMergePreview         = false;
    this.MailMergeFieldsHighlight = false; // Подсвечивать ли все поля связанные с рассылкой
    this.MailMergeFields          = [];

    // Класс, управляющий полями
    this.FieldsManager = new CDocumentFieldsManager();

    // Класс, управляющий закладками
	this.BookmarksManager = new CBookmarksManager(this);

    // Режим рецензирования
    this.TrackRevisions = false;
    this.TrackRevisionsManager = new CTrackRevisionsManager(this);

    // Контролируем изменения интерфейса
    this.ChangedStyles      = []; // Объект с Id стилями, которые были изменены/удалены/добавлены
	this.TurnOffPanelStyles = 0;  // == 0 - можно обновлять панельку со стилями, != 0 - нельзя обновлять

    // Добавляем данный класс в таблицу Id (обязательно в конце конструктора)
    this.TableId.Add(this, this.Id);

	// Объект для составного ввода текста
	this.CompositeInput = null;

	// Нужно ли проверять тип лока у ContentControl при проверке залоченности выделенных объектов
	this.CheckContentControlsLock = true;

	this.ViewModeInReview = {
		mode                : 0,     // -1 - исходный, 0 - со всеми изменениями, 1 - результат
		isFastCollaboration : false
	};

	// Класс для работы со сносками
	this.Footnotes               = new CFootnotesController(this);
	this.LogicDocumentController = new CLogicDocumentController(this);
	this.DrawingsController      = new CDrawingsController(this, this.DrawingObjects);
	this.HeaderFooterController  = new CHdrFtrController(this, this.HdrFtr);
	
	this.Controller = this.LogicDocumentController;

    this.StartTime = 0;
}
CDocument.prototype = Object.create(CDocumentContentBase.prototype);
CDocument.prototype.constructor = CDocument;

CDocument.prototype.Init                           = function()
{

};
CDocument.prototype.On_EndLoad                     = function()
{
    // Обновляем информацию о секциях
    this.Update_SectionsInfo();

    // Проверяем последний параграф на наличие секции
    this.Check_SectionLastParagraph();

    // Специальная проверка плохо заданных нумераций через стиль. Когда ссылка на нумерацию в стиле есть,
    // а обратной ссылки в нумерации на стиль - нет.
    this.Styles.Check_StyleNumberingOnLoad(this.Numbering);

    // Перемещаем курсор в начало документа
    this.MoveCursorToStartPos(false);

    if (editor.DocInfo)
    {
        var TemplateReplacementData = editor.DocInfo.get_TemplateReplacement();
        if (null !== TemplateReplacementData)
        {
            this.private_ProcessTemplateReplacement(TemplateReplacementData);
        }
    }
    if (null !== this.CollaborativeEditing)
    {
        this.Set_FastCollaborativeEditing(true);
    }
};
CDocument.prototype.Add_TestDocument               = function()
{
    this.Content   = [];
    var Text       = ["Comparison view helps you track down memory leaks, by displaying which objects have been correctly cleaned up by the garbage collector. Generally used to record and compare two (or more) memory snapshots of before and after an operation. The idea is that inspecting the delta in freed memory and reference count lets you confirm the presence and cause of a memory leak.", "Containment view provides a better view of object structure, helping us analyse objects referenced in the global namespace (i.e. window) to find out what is keeping them around. It lets you analyse closures and dive into your objects at a low level.", "Dominators view helps confirm that no unexpected references to objects are still hanging around (i.e that they are well contained) and that deletion/garbage collection is actually working."];
    var ParasCount = 50;
    var RunsCount  = Text.length;
    for (var ParaIndex = 0; ParaIndex < ParasCount; ParaIndex++)
    {
        var Para = new Paragraph(this.DrawingDocument, this);
        //var Run = new ParaRun(Para);
        for (var RunIndex = 0; RunIndex < RunsCount; RunIndex++)
        {

            var String    = Text[RunIndex];
            var StringLen = String.length;
            for (var TextIndex = 0; TextIndex < StringLen; TextIndex++)
            {
                var Run         = new ParaRun(Para);
                var TextElement = String[TextIndex];

                var Element = (TextElement !== " " ? new ParaText(TextElement) : new ParaSpace() );
                Run.Add_ToContent(TextIndex, Element, false);
                Para.Add_ToContent(0, Run);
            }


        }
        //Para.Add_ToContent(0, Run);
        this.Internal_Content_Add(this.Content.length, Para);
    }

	this.Recalculate_FromStart(true);
};
CDocument.prototype.LoadEmptyDocument              = function()
{
    this.DrawingDocument.TargetStart();
    this.Recalculate();

    this.Interface_Update_ParaPr();
    this.Interface_Update_TextPr();
};
CDocument.prototype.Set_CurrentElement = function(Index, bUpdateStates)
{
	var OldDocPosType = this.CurPos.Type;

	var ContentPos = Math.max(0, Math.min(this.Content.length - 1, Index));

	this.Set_DocPosType(docpostype_Content);
	this.CurPos.ContentPos = Math.max(0, Math.min(this.Content.length - 1, Index));

	this.Reset_WordSelection();
	if (true === this.Content[ContentPos].IsSelectionUse())
	{
		this.Selection.Flag     = selectionflag_Common;
		this.Selection.Use      = true;
		this.Selection.StartPos = ContentPos;
		this.Selection.EndPos   = ContentPos;
	}
	else
		this.RemoveSelection();

	if (false != bUpdateStates)
	{
		this.Document_UpdateInterfaceState();
		this.Document_UpdateRulersState();
		this.Document_UpdateSelectionState();
	}

	if (docpostype_HdrFtr === OldDocPosType)
	{
		this.DrawingDocument.ClearCachePages();
		this.DrawingDocument.FirePaint();
	}
};
CDocument.prototype.Is_ThisElementCurrent          = function()
{
    return true;
};
CDocument.prototype.Get_PageContentStartPos        = function(PageIndex, ElementIndex)
{
    if (undefined === ElementIndex && undefined !== this.Pages[PageIndex])
        ElementIndex = this.Pages[PageIndex].Pos;

    var SectPr = this.SectionsInfo.Get_SectPr(ElementIndex).SectPr;

    var Y      = SectPr.PageMargins.Top;
    var YLimit = SectPr.PageSize.H - SectPr.PageMargins.Bottom;
    var X      = SectPr.PageMargins.Left;
    var XLimit = SectPr.PageSize.W - SectPr.PageMargins.Right;

    var HdrFtrLine = this.HdrFtr.Get_HdrFtrLines(PageIndex);

    var YHeader = HdrFtrLine.Top;
    if (null !== YHeader && YHeader > Y)
        Y = YHeader;

    var YFooter = HdrFtrLine.Bottom;
    if (null !== YFooter && YFooter < YLimit)
        YLimit = YFooter;

    return {X : X, Y : Y, XLimit : XLimit, YLimit : YLimit};
};
CDocument.prototype.Get_PageContentStartPos2       = function(StartPageIndex, StartColumnIndex, ElementPageIndex, ElementIndex)
{
    if (undefined === ElementIndex && undefined !== this.Pages[StartPageIndex])
        ElementIndex = this.Pages[StartPageIndex].Pos;

    var SectPr = this.SectionsInfo.Get_SectPr(ElementIndex).SectPr;

    var ColumnsCount = SectPr.Get_ColumnsCount();
    var ColumnAbs    = (StartColumnIndex + ElementPageIndex) - ((StartColumnIndex + ElementPageIndex) / ColumnsCount | 0) * ColumnsCount;
    var PageAbs      = StartPageIndex + ((StartColumnIndex + ElementPageIndex) / ColumnsCount | 0);

	var Y      = SectPr.Get_PageMargin_Top();
	var YLimit = SectPr.Get_PageHeight() - SectPr.Get_PageMargin_Bottom();
	var X      = SectPr.Get_PageMargin_Left();
	var XLimit = SectPr.Get_PageWidth() - SectPr.Get_PageMargin_Right();


	var SectionIndex = this.FullRecalc.SectionIndex;
    if (this.Pages[PageAbs] && this.Pages[PageAbs].Sections[SectionIndex])
    {
        Y      = this.Pages[PageAbs].Sections[SectionIndex].Get_Y();
        YLimit = this.Pages[PageAbs].Sections[SectionIndex].Get_YLimit();
    }

    var HdrFtrLine = this.HdrFtr.Get_HdrFtrLines(PageAbs);

    for (var ColumnIndex = 0; ColumnIndex < ColumnAbs; ++ColumnIndex)
    {
        X += SectPr.Get_ColumnWidth(ColumnIndex);
        X += SectPr.Get_ColumnSpace(ColumnIndex);
    }

    if (ColumnsCount - 1 !== ColumnAbs)
        XLimit = X + SectPr.Get_ColumnWidth(ColumnAbs);

    var YHeader = HdrFtrLine.Top;
    if (null !== YHeader && YHeader > Y)
        Y = YHeader;

    var YFooter = HdrFtrLine.Bottom;
    if (null !== YFooter && YFooter < YLimit)
        YLimit = YFooter;

    var ColumnSpaceBefore = (ColumnAbs > 0 ? SectPr.Get_ColumnSpace(ColumnAbs - 1) : 0);
    var ColumnSpaceAfter  = (ColumnAbs < ColumnsCount - 1 ? SectPr.Get_ColumnSpace(ColumnAbs) : 0);

    return {
        X                 : X,
        Y                 : Y,
        XLimit            : XLimit,
        YLimit            : YLimit,
        ColumnSpaceBefore : ColumnSpaceBefore,
        ColumnSpaceAfter  : ColumnSpaceAfter
    };
};
CDocument.prototype.Get_PageLimits                 = function(PageIndex)
{
    var Index  = ( undefined !== this.Pages[PageIndex] ? this.Pages[PageIndex].Pos : 0 );
    var SectPr = this.SectionsInfo.Get_SectPr(Index).SectPr;

    var W = SectPr.Get_PageWidth();
    var H = SectPr.Get_PageHeight();

    return {X : 0, Y : 0, XLimit : W, YLimit : H};
};
CDocument.prototype.Get_PageFields                 = function(PageIndex)
{
    var Index  = ( undefined !== this.Pages[PageIndex] ? this.Pages[PageIndex].Pos : 0 );
    var SectPr = this.SectionsInfo.Get_SectPr(Index).SectPr;

    var Y      = SectPr.PageMargins.Top;
    var YLimit = SectPr.PageSize.H - SectPr.PageMargins.Bottom;
    var X      = SectPr.PageMargins.Left;
    var XLimit = SectPr.PageSize.W - SectPr.PageMargins.Right;

    return {X : X, Y : Y, XLimit : XLimit, YLimit : YLimit};
};
CDocument.prototype.Get_ColumnFields               = function(ElementIndex, ColumnIndex)
{
    var SectPr = this.SectionsInfo.Get_SectPr(ElementIndex).SectPr;

    var Y      = SectPr.Get_PageMargin_Top();
    var YLimit = SectPr.Get_PageHeight() - SectPr.Get_PageMargin_Bottom();
    var X      = SectPr.Get_PageMargin_Left();
    var XLimit = SectPr.Get_PageWidth() - SectPr.Get_PageMargin_Right();

    var ColumnsCount = SectPr.Get_ColumnsCount();
    if (ColumnIndex >= ColumnsCount)
        ColumnIndex = ColumnsCount - 1;

    for (var ColIndex = 0; ColIndex < ColumnIndex; ++ColIndex)
    {
        X += SectPr.Get_ColumnWidth(ColIndex);
        X += SectPr.Get_ColumnSpace(ColIndex);
    }

    if (ColumnsCount - 1 !== ColumnIndex)
        XLimit = X + SectPr.Get_ColumnWidth(ColumnIndex);

    return {X : X, XLimit : XLimit};
};
CDocument.prototype.Get_Theme                      = function()
{
    return this.theme;
};
CDocument.prototype.Get_ColorMap                   = function()
{
    return this.clrSchemeMap;
};
CDocument.prototype.Get_AllBoundsRectOnPageForMath = function(nPageIndex)
{
    return this.DrawingObjects.getAllBoundsRectOnPageForMath(nPageIndex);
};
/**
 * Данная функция предназначена для отключения пересчета. Это может быть полезно, т.к. редактор всегда запускает
 * пересчет после каждого действия.
 */
CDocument.prototype.TurnOff_Recalculate = function()
{
    this.TurnOffRecalc++;
};
/**
 * Включаем пересчет, если он был отключен.
 * @param {boolean} bRecalculate Запускать ли пересчет
 */
CDocument.prototype.TurnOn_Recalculate = function(bRecalculate)
{
    this.TurnOffRecalc--;

    if (bRecalculate)
        this.Recalculate();
};
/**
 * Проверяем включен ли пересчет.
 * @returns {boolean}
 */
CDocument.prototype.Is_OnRecalculate = function()
{
    if (0 === this.TurnOffRecalc)
        return true;

    return false;
};
/**
 * Запускаем пересчет документа.
 * @param bOneParagraph
 * @param bRecalcContentLast
 * @param _RecalcData
 */
CDocument.prototype.Recalculate = function(bOneParagraph, bRecalcContentLast, _RecalcData)
{
	if (this.RecalcInfo.Is_NeedRecalculateFromStart())
	{
		this.RecalcInfo.Set_NeedRecalculateFromStart(false);
		this.Recalculate_FromStart();
		return;
	}

    this.StartTime = new Date().getTime();

    if (true !== this.Is_OnRecalculate())
        return;

    // Останавливаем поиск
    if (false != this.SearchEngine.ClearOnRecalc)
    {
        var bOldSearch = ( this.SearchEngine.Count > 0 ? true : false );

        this.SearchEngine.Clear();

        if (true === bOldSearch)
        {
            editor.sync_SearchEndCallback();

            this.DrawingDocument.ClearCachePages();
            this.DrawingDocument.FirePaint();
        }
    }

    // Обновляем позицию курсора
    this.NeedUpdateTarget = true;

    // Увеличиваем номер пересчета
    this.RecalcId++;

    // Если задан параметр _RecalcData, тогда мы не можем ориентироваться на историю
    if (undefined === _RecalcData)
    {
        // Проверяем можно ли сделать быстрый пересчет
        var SimpleChanges = History.Is_SimpleChanges();
        if (1 === SimpleChanges.length)
        {
            var Run  = SimpleChanges[0].Class;
            var Para = Run.Paragraph;

            var PageIndex = Para.Recalculate_FastRange(SimpleChanges);
            if (-1 !== PageIndex && this.Pages[PageIndex])
            {
                // Если за данным параграфом следовал пустой параграф с новой секцией, тогда его тоже надо пересчитать.
                var NextElement = Para.Get_DocumentNext();
                if (null !== NextElement && true === this.Pages[PageIndex].Check_EndSectionPara(NextElement))
                    this.private_RecalculateEmptySectionParagraph(NextElement, Para, PageIndex, Para.Get_AbsoluteColumn(Para.Get_PagesCount() - 1), Para.Get_ColumnsCount());

                // Перерисуем страницу, на которой произошли изменения
                this.DrawingDocument.OnRecalculatePage(PageIndex, this.Pages[PageIndex]);
                this.DrawingDocument.OnEndRecalculate(false, true);
                History.Reset_RecalcIndex();
                this.private_UpdateCursorXY(true, true);

                if (Para.Parent && Para.Parent.Get_TopDocumentContent)
				{
					var oTopDocument = Para.Parent.Get_TopDocumentContent();
					if (oTopDocument instanceof CFootEndnote)
						oTopDocument.OnFastRecalculate();
				}

                return;
            }
        }

        // TODO: Тут надо вставить заглушку, что если у нас в долгом пересчете находится страница <= PageIndex + 1,
        //       по отношению к данной, тогда не надо делать быстрый пересчет.
        var SimplePara = History.Is_ParagraphSimpleChanges();
        if (null !== SimplePara)
        {
            var FastPages      = SimplePara.Recalculate_FastWholeParagraph();
            var FastPagesCount = FastPages.length;

            var bCanRecalc = true;
            for (var Index = 0; Index < FastPagesCount; Index++)
			{
				if (!this.Pages[FastPages[Index]])
				{
					bCanRecalc = false;
					break;
				}
			}

            if (FastPagesCount > 0 && true === bCanRecalc)
            {
                // Если изменения произошли на последней странице параграфа, и за данным параграфом следовал
                // пустой параграф с новой секцией, тогда его тоже надо пересчитать.
                var NextElement  = SimplePara.Get_DocumentNext();
                var LastFastPage = FastPages[FastPagesCount - 1];
                if (null !== NextElement && true === this.Pages[LastFastPage].Check_EndSectionPara(NextElement))
                    this.private_RecalculateEmptySectionParagraph(NextElement, SimplePara, LastFastPage, SimplePara.Get_AbsoluteColumn(SimplePara.Get_PagesCount() - 1), SimplePara.Get_ColumnsCount());

                for (var Index = 0; Index < FastPagesCount; Index++)
                {
                    var PageIndex = FastPages[Index];
                    this.DrawingDocument.OnRecalculatePage(PageIndex, this.Pages[PageIndex]);
                }

                this.DrawingDocument.OnEndRecalculate(false, true);
                History.Reset_RecalcIndex();
                this.private_UpdateCursorXY(true, true);

                if (SimplePara.Parent && SimplePara.Parent.Get_TopDocumentContent)
				{
					var oTopDocument = SimplePara.Parent.Get_TopDocumentContent();
					if (oTopDocument instanceof CFootEndnote)
						oTopDocument.OnFastRecalculate();
				}

				return;
            }
        }
    }

    //console.log( "Long Recalc " );

    var ChangeIndex = 0;
    var MainChange  = false;

    // Получаем данные об произошедших изменениях
    var RecalcData = History.Get_RecalcData(_RecalcData);

    History.Reset_RecalcIndex();

    this.DrawingObjects.recalculate_(RecalcData.Drawings);
    this.DrawingObjects.recalculateText_(RecalcData.Drawings);

    // 1. Пересчитываем все автофигуры, которые нужно пересчитать. Изменения в них ни на что не влияют.
    for (var GraphIndex = 0; GraphIndex < RecalcData.Flow.length; GraphIndex++)
    {
        RecalcData.Flow[GraphIndex].recalculateDocContent();
    }

    // 2. Просмотрим все колонтитулы, которые подверглись изменениям. Найдем стартовую страницу, с которой надо
    //    запустить пересчет.

    var SectPrIndex = -1;
    for (var HdrFtrIndex = 0; HdrFtrIndex < RecalcData.HdrFtr.length; HdrFtrIndex++)
    {
        var HdrFtr    = RecalcData.HdrFtr[HdrFtrIndex];
        var FindIndex = this.SectionsInfo.Find_ByHdrFtr(HdrFtr);

        if (-1 === FindIndex)
            continue;

        // Колонтитул может быть записан в данной секции, но в ней не использоваться. Нам нужно начинать пересчет
        // с места использования данного колонтитула.

        var SectPr     = this.SectionsInfo.Get_SectPr2(FindIndex).SectPr;
        var HdrFtrInfo = SectPr.Get_HdrFtrInfo(HdrFtr);

        if (null !== HdrFtrInfo)
        {
            var bHeader = HdrFtrInfo.Header;
            var bFirst  = HdrFtrInfo.First;
            var bEven   = HdrFtrInfo.Even;

            var CheckSectIndex = -1;

            if (true === bFirst)
            {
                var CurSectIndex = FindIndex;
                var SectCount    = this.SectionsInfo.Elements.length;

                while (CurSectIndex < SectCount)
                {
                    var CurSectPr = this.SectionsInfo.Get_SectPr2(CurSectIndex).SectPr;

                    if (FindIndex === CurSectIndex || null === CurSectPr.Get_HdrFtr(bHeader, bFirst, bEven))
                    {
                        if (true === CurSectPr.Get_TitlePage())
                        {
                            CheckSectIndex = CurSectIndex;
                            break;
                        }

                    }
                    else
                    {
                        // Если мы попали сюда, значит данный колонтитул нигде не используется
                        break;
                    }

                    CurSectIndex++;
                }
            }
            else if (true === bEven)
            {
                if (true === EvenAndOddHeaders)
                    CheckSectIndex = FindIndex;
            }
            else
            {
                CheckSectIndex = FindIndex;
            }

            if (-1 !== CheckSectIndex && ( -1 === SectPrIndex || CheckSectIndex < SectPrIndex ))
                SectPrIndex = CheckSectIndex;
        }
    }

	if (-1 === RecalcData.Inline.Pos && -1 === SectPrIndex)
	{
		// Никаких изменений не было ни с самим документом, ни секциями
		ChangeIndex               = -1;
		RecalcData.Inline.PageNum = 0;
	}
	else if (-1 === RecalcData.Inline.Pos)
	{
		// Были изменения только внутри секций
		MainChange = false;

		// Выставляем начало изменений на начало секции
		ChangeIndex               = ( 0 === SectPrIndex ? 0 : this.SectionsInfo.Get_SectPr2(SectPrIndex - 1).Index + 1 );
		RecalcData.Inline.PageNum = 0;
	}
	else if (-1 === SectPrIndex)
	{
		// Изменения произошли только внутри основного документа
		MainChange = true;

		ChangeIndex = RecalcData.Inline.Pos;
	}
	else
	{
		// Изменения произошли и внутри документа, и внутри секций. Смотрим на более ранюю точку начала изменений
		// для секций и основоной части документа.
		MainChange = true;

		ChangeIndex = RecalcData.Inline.Pos;

		var ChangeIndex2 = ( 0 === SectPrIndex ? 0 : this.SectionsInfo.Get_SectPr2(SectPrIndex - 1).Index + 1 );

		if (ChangeIndex2 <= ChangeIndex)
		{
			ChangeIndex               = ChangeIndex2;
			RecalcData.Inline.PageNum = 0;
		}
	}

	// Найдем начальную страницу, с которой мы начнем пересчет
	var StartPage  = 0;
	var StartIndex = 0;

	if (ChangeIndex < 0 && true === RecalcData.NotesEnd)
	{
		// Сюда мы попадаем при рассчете сносок, которые выходят за пределы самого документа
		StartIndex = this.Content.length;
		StartPage  = RecalcData.NotesEndPage;
		MainChange = true;
	}
	else
	{
		if (ChangeIndex < 0)
		{
			this.DrawingDocument.ClearCachePages();
			this.DrawingDocument.FirePaint();
			return;
		}
		else if (ChangeIndex >= this.Content.length)
		{
			ChangeIndex = this.Content.length - 1;
		}

		// Здсь мы должны проверить предыдущие элементы на наличие параматра KeepNext
		while (ChangeIndex > 0)
		{
			var PrevElement = this.Content[ChangeIndex - 1];
			if (type_Paragraph === PrevElement.Get_Type() && true === PrevElement.Get_CompiledPr2(false).ParaPr.KeepNext)
			{
				ChangeIndex--;
				RecalcData.Inline.PageNum = PrevElement.Get_StartPage_Absolute() + (PrevElement.Pages.length - 1);
				// считаем, что изменилась последняя страница
			}
			else
			{
				break;
			}
		}

		var ChangedElement = this.Content[ChangeIndex];
		if (ChangedElement.GetPagesCount() > 0 && -1 !== ChangedElement.GetIndex() && ChangedElement.Get_StartPage_Absolute() < RecalcData.Inline.PageNum - 1)
		{
			StartIndex = ChangeIndex;
			StartPage  = RecalcData.Inline.PageNum - 1;
		}
		else
		{
			var PagesCount = this.Pages.length;
			for (var PageIndex = 0; PageIndex < PagesCount; PageIndex++)
			{
				if (ChangeIndex > this.Pages[PageIndex].Pos)
				{
					StartPage  = PageIndex;
					StartIndex = this.Pages[PageIndex].Pos;
				}
				else
					break;
			}

			if (ChangeIndex === StartIndex && StartPage < RecalcData.Inline.PageNum)
				StartPage = RecalcData.Inline.PageNum - 1;
		}

		// Если у нас уже начался долгий пересчет, тогда мы его останавливаем, и запускаем новый с текущими параметрами.
		// Здесь возможен случай, когда мы долгий пересчет основной части документа останавливаем из-за пересчета
		// колонтитулов, в этом случае параметр MainContentPos не меняется, и мы будем пересчитывать только колонтитулы
		// либо до страницы, на которой они приводят к изменению основную часть документа, либо до страницы, где
		// остановился предыдущий пересчет.

		if (null != this.FullRecalc.Id)
		{
			clearTimeout(this.FullRecalc.Id);
			this.FullRecalc.Id = null;
			this.DrawingDocument.OnEndRecalculate(false);

			if (this.FullRecalc.StartIndex < StartIndex)
			{
				StartIndex = this.FullRecalc.StartIndex;
				StartPage  = this.FullRecalc.PageIndex;
			}
		}
		else if (null !== this.HdrFtrRecalc.Id)
		{
			clearTimeout(this.HdrFtrRecalc.Id);
			this.HdrFtrRecalc.Id = null;
			this.DrawingDocument.OnEndRecalculate(false);
		}
	}

	this.HdrFtrRecalc.PageCount = -1;

    // Очищаем данные пересчета
    this.RecalcInfo.Reset();

    this.FullRecalc.PageIndex         = StartPage;
    this.FullRecalc.SectionIndex      = 0;
    this.FullRecalc.ColumnIndex       = 0;
    this.FullRecalc.StartIndex        = StartIndex;
    this.FullRecalc.Start             = true;
    this.FullRecalc.StartPage         = StartPage;
    this.FullRecalc.ResetStartElement = this.private_RecalculateIsNewSection(StartPage, StartIndex);

    // Если у нас произошли какие-либо изменения с основной частью документа, тогда начинаем его пересчитывать сразу,
    // а если изменения касались только секций, тогда пересчитываем основную часть документа только с того места, где
    // остановился предыдущий пересчет, либо с того места, где изменения секций приводят к пересчету документа.
    if (true === MainChange)
        this.FullRecalc.MainStartPos = StartIndex;

    this.DrawingDocument.OnStartRecalculate(StartPage);
    this.Recalculate_Page();
};
/**
 * Пересчитываем следующую страницу.
 */
CDocument.prototype.Recalculate_Page = function()
{
    var SectionIndex = this.FullRecalc.SectionIndex;
    var PageIndex    = this.FullRecalc.PageIndex;
    var ColumnIndex  = this.FullRecalc.ColumnIndex;
    var bStart       = this.FullRecalc.Start;        // флаг, который говорит о том, рассчитываем мы эту страницу первый раз или нет (за один общий пересчет)
    var StartIndex   = this.FullRecalc.StartIndex;

    if (0 === SectionIndex && 0 === ColumnIndex && true === bStart)
    {
        var OldPage = ( undefined !== this.Pages[PageIndex] ? this.Pages[PageIndex] : null );

        if (true === bStart)
        {
            var Page              = new CDocumentPage();
            this.Pages[PageIndex] = Page;
            Page.Pos              = StartIndex;

            if (true === this.HdrFtr.Recalculate(PageIndex))
                this.FullRecalc.MainStartPos = StartIndex;

            var SectPr = this.SectionsInfo.Get_SectPr(StartIndex).SectPr;

            Page.Width          = SectPr.PageSize.W;
            Page.Height         = SectPr.PageSize.H;
            Page.Margins.Left   = SectPr.PageMargins.Left;
            Page.Margins.Top    = SectPr.PageMargins.Top;
            Page.Margins.Right  = SectPr.PageSize.W - SectPr.PageMargins.Right;
            Page.Margins.Bottom = SectPr.PageSize.H - SectPr.PageMargins.Bottom;

            Page.Sections[0] = new CDocumentPageSection();
            var ColumnsCount = SectPr.Get_ColumnsCount();
            for (var ColumnIndex = 0; ColumnIndex < ColumnsCount; ++ColumnIndex)
            {
                Page.Sections[0].Columns[ColumnIndex] = new CDocumentPageColumn();
            }
            Page.Sections[0].ColumnsSep = SectPr.Get_ColumnsSep();
        }

        var Count = this.Content.length;

        // Проверяем нужно ли пересчитывать основную часть документа на данной странице
        var MainStartPos = this.FullRecalc.MainStartPos;
        if (null !== OldPage && ( -1 === MainStartPos || MainStartPos > StartIndex ))
        {
            if (OldPage.EndPos >= Count - 1 && PageIndex - this.Content[Count - 1].Get_StartPage_Absolute() >= this.Content[Count - 1].GetPagesCount() - 1)
            {
                //console.log( "HdrFtr Recalc " + PageIndex );

                this.Pages[PageIndex] = OldPage;
                this.DrawingDocument.OnRecalculatePage(PageIndex, this.Pages[PageIndex]);

                this.private_CheckCurPage();
                this.DrawingDocument.OnEndRecalculate(true);
                this.DrawingObjects.onEndRecalculateDocument(this.Pages.length);

                if (true === this.Selection.UpdateOnRecalc)
                {
                    this.Selection.UpdateOnRecalc = false;
                    this.DrawingDocument.OnSelectEnd();
                }

                this.FullRecalc.Id           = null;
                this.FullRecalc.MainStartPos = -1;

                return;
            }
            else if (undefined !== this.Pages[PageIndex + 1])
            {
                //console.log( "HdrFtr Recalc " + PageIndex );

                // Переходим к следующей странице
                this.Pages[PageIndex] = OldPage;
                this.DrawingDocument.OnRecalculatePage(PageIndex, this.Pages[PageIndex]);

                this.FullRecalc.PageIndex         = PageIndex + 1;
                this.FullRecalc.Start             = true;
                this.FullRecalc.StartIndex        = this.Pages[PageIndex + 1].Pos;
                this.FullRecalc.ResetStartElement = false;

                var CurSectInfo  = this.SectionsInfo.Get_SectPr(this.Pages[PageIndex + 1].Pos);
                var PrevSectInfo = this.SectionsInfo.Get_SectPr(this.Pages[PageIndex].EndPos);

                if (PrevSectInfo !== CurSectInfo)
                    this.FullRecalc.ResetStartElement = true;

                if (window["NATIVE_EDITOR_ENJINE_SYNC_RECALC"] === true)
                {
                    if (PageIndex + 1 > this.FullRecalc.StartPage + 2)
                    {
                        if (window["native"]["WC_CheckSuspendRecalculate"] !== undefined)
                        {
                            //if (window["native"]["WC_CheckSuspendRecalculate"]())
                            //    return;

                            this.FullRecalc.Id = setTimeout(Document_Recalculate_Page, 10);
                            return;
                        }
                    }

                    this.Recalculate_Page();
                    return;
                }

                if (PageIndex + 1 > this.FullRecalc.StartPage + 2)
                {
                    this.FullRecalc.Id = setTimeout(Document_Recalculate_Page, 20);
                }
                else
                    this.Recalculate_Page();

                return;
            }
        }
        else
        {
            if (true === bStart)
            {
                this.Pages.length = PageIndex + 1;

                this.DrawingObjects.createGraphicPage(PageIndex);
                this.DrawingObjects.resetDrawingArrays(PageIndex, this);
            }
        }

        //console.log( "Regular Recalc " + PageIndex );

        var StartPos = this.Get_PageContentStartPos(PageIndex, StartIndex);

		this.Footnotes.Reset(PageIndex, this.SectionsInfo.Get_SectPr(StartIndex).SectPr);

        this.Pages[PageIndex].ResetStartElement = this.FullRecalc.ResetStartElement;
        this.Pages[PageIndex].X                 = StartPos.X;
        this.Pages[PageIndex].XLimit            = StartPos.XLimit;
        this.Pages[PageIndex].Y                 = StartPos.Y;
        this.Pages[PageIndex].YLimit            = StartPos.YLimit;

        this.Pages[PageIndex].Sections[0].Y      = StartPos.Y;
        this.Pages[PageIndex].Sections[0].YLimit = StartPos.YLimit;
        this.Pages[PageIndex].Sections[0].Pos    = StartIndex;
        this.Pages[PageIndex].Sections[0].EndPos = StartIndex;
    }

    this.Recalculate_PageColumn();
};
/**
 * Пересчитываем следующую колоноку.
 */
CDocument.prototype.Recalculate_PageColumn                   = function()
{
    var PageIndex          = this.FullRecalc.PageIndex;
    var SectionIndex       = this.FullRecalc.SectionIndex;
    var ColumnIndex        = this.FullRecalc.ColumnIndex;
    var StartIndex         = this.FullRecalc.StartIndex;
    var bResetStartElement = this.FullRecalc.ResetStartElement;

     // console.log("Page " + PageIndex + " Section " + SectionIndex + " Column " + ColumnIndex + " Element " + StartIndex);
     // console.log(this.RecalcInfo);

    var StartPos = this.Get_PageContentStartPos2(PageIndex, ColumnIndex, 0, StartIndex);

    var X      = StartPos.X;
    var Y      = StartPos.Y;
    var YLimit = StartPos.YLimit;
    var XLimit = StartPos.XLimit;

    var Page        = this.Pages[PageIndex];
    var PageSection = Page.Sections[SectionIndex];
    var PageColumn  = PageSection.Columns[ColumnIndex];

    PageColumn.X           = X;
    PageColumn.XLimit      = XLimit;
    PageColumn.Y           = Y;
    PageColumn.YLimit      = YLimit;
    PageColumn.Pos         = StartIndex;
    PageColumn.Empty       = false;
    PageColumn.SpaceBefore = StartPos.ColumnSpaceBefore;
    PageColumn.SpaceAfter  = StartPos.ColumnSpaceAfter;

    this.Footnotes.ContinueElementsFromPreviousColumn(PageIndex, ColumnIndex, Y, YLimit);

    var SectElement  = this.SectionsInfo.Get_SectPr(StartIndex);
    var SectPr       = SectElement.SectPr;
    var ColumnsCount = SectPr.Get_ColumnsCount();

    var bReDraw             = true;
    var bContinue           = false;
    var _PageIndex          = PageIndex;
    var _ColumnIndex        = ColumnIndex;
    var _StartIndex         = StartIndex;
    var _SectionIndex       = SectionIndex;
    var _bStart             = false;
    var _bResetStartElement = false;

    var Count = this.Content.length;
    var Index;
    for (Index = StartIndex; Index < Count; ++Index)
    {
        // Пересчитываем элемент документа
        var Element = this.Content[Index];

        var RecalcResult = recalcresult_NextElement;
        var bFlow        = false;

        if (true !== Element.Is_Inline())
        {
            bFlow = true;

            // Проверяем PageBreak и ColumnBreak в предыдущей строке
            var isPageBreakOnPrevLine   = false;
            var isColumnBreakOnPrevLine = false;

            var PrevElement = Element.Get_DocumentPrev();

            if (null !== PrevElement && type_Paragraph === PrevElement.Get_Type() && true === PrevElement.Is_Empty() && undefined !== PrevElement.Get_SectionPr())
                PrevElement = PrevElement.Get_DocumentPrev();

            if (null !== PrevElement && type_Paragraph === PrevElement.Get_Type())
            {
                var bNeedPageBreak = true;
                if (undefined !== PrevElement.Get_SectionPr())
                {
                    var PrevSectPr = PrevElement.Get_SectionPr();
                    var CurSectPr  = this.SectionsInfo.Get_SectPr(Index).SectPr;
                    if (c_oAscSectionBreakType.Continuous !== CurSectPr.Get_Type() || true !== CurSectPr.Compare_PageSize(PrevSectPr))
                        bNeedPageBreak = false;
                }

                var EndLine = PrevElement.Pages[PrevElement.Pages.length - 1].EndLine;
                if (true === bNeedPageBreak && -1 !== EndLine && PrevElement.Lines[EndLine].Info & paralineinfo_BreakRealPage && Index !== Page.Pos)
                    isPageBreakOnPrevLine = true;

                if (-1 !== EndLine && !(PrevElement.Lines[EndLine].Info & paralineinfo_BreakRealPage) && PrevElement.Lines[EndLine].Info & paralineinfo_BreakPage && Index !== PageColumn.Pos)
                    isColumnBreakOnPrevLine = true;
            }

            if (true === isColumnBreakOnPrevLine)
            {
                RecalcResult = recalcresult_NextPage | recalcresultflags_LastFromNewColumn;
            }
            else if (true === isPageBreakOnPrevLine)
            {
                RecalcResult = recalcresult_NextPage | recalcresultflags_LastFromNewPage;
            }
            else
            {
                var RecalcInfo =
                    {
                        Element           : Element,
                        X                 : X,
                        Y                 : Y,
                        XLimit            : XLimit,
                        YLimit            : YLimit,
                        PageIndex         : PageIndex,
                        SectionIndex      : SectionIndex,
                        ColumnIndex       : ColumnIndex,
                        Index             : Index,
                        StartIndex        : StartIndex,
                        ColumnsCount      : ColumnsCount,
                        ResetStartElement : bResetStartElement,
                        RecalcResult      : RecalcResult
                    };

                if (type_Table === Element.GetType())
                    this.private_RecalculateFlowTable(RecalcInfo);
                else if (type_Paragraph === Element.Get_Type())
                    this.private_RecalculateFlowParagraph(RecalcInfo);

                Index        = RecalcInfo.Index;
                RecalcResult = RecalcInfo.RecalcResult;
            }
        }
        else
        {
            if ((0 === Index && 0 === PageIndex && 0 === ColumnIndex) || Index != StartIndex || (Index === StartIndex && true === bResetStartElement))
            {
                Element.Set_DocumentIndex(Index);
                Element.Reset(X, Y, XLimit, YLimit, PageIndex, ColumnIndex, ColumnsCount);
            }

            // Делаем как в Word: Обработаем особый случай, когда на данном параграфе заканчивается секция, и он
            // пустой. В такой ситуации этот параграф не добавляет смещения по Y, и сам приписывается в конец
            // предыдущего элемента. Второй подряд идущий такой же параграф обсчитывается по обычному.

            var SectInfoElement = this.SectionsInfo.Get_SectPr(Index);
            var PrevElement     = this.Content[Index - 1]; // может быть undefined, но в следующем условии сразу стоит проверка на Index > 0
            if (Index > 0 && ( Index !== StartIndex || true !== bResetStartElement ) && Index === SectInfoElement.Index && true === Element.IsEmpty() && ( type_Paragraph !== PrevElement.GetType() || undefined === PrevElement.Get_SectionPr() ))
            {
                RecalcResult = recalcresult_NextElement;

                this.private_RecalculateEmptySectionParagraph(Element, PrevElement, PageIndex, ColumnIndex, ColumnsCount);

                // Добавим в список особых параграфов
                this.Pages[PageIndex].EndSectionParas.push(Element);

                // Выставляем этот флаг, чтобы у нас не менялось значение по Y
                bFlow = true;
            }
            else
            {
                var ElementPageIndex = this.private_GetElementPageIndex(Index, PageIndex, ColumnIndex, ColumnsCount);
                RecalcResult         = Element.Recalculate_Page(ElementPageIndex);
            }
        }

        if (true != bFlow && (RecalcResult & recalcresult_NextElement || RecalcResult & recalcresult_NextPage))
        {
            var ElementPageIndex = this.private_GetElementPageIndex(Index, PageIndex, ColumnIndex, ColumnsCount);
            Y                    = Element.Get_PageBounds(ElementPageIndex).Bottom;
        }

        PageColumn.Bounds.Bottom = Y;

        if (RecalcResult & recalcresult_CurPage)
        {
            bReDraw       = false;
            bContinue     = true;
            _PageIndex    = PageIndex;
            _SectionIndex = SectionIndex;
            _bStart       = false;

            if (RecalcResult & recalcresultflags_Column)
            {
                _ColumnIndex = ColumnIndex;
                _StartIndex  = StartIndex;
            }
            else
            {
                _ColumnIndex = 0;
                _StartIndex  = this.Pages[_PageIndex].Sections[_SectionIndex].Columns[0].Pos;
            }

            break;
        }
        else if (RecalcResult & recalcresult_NextElement)
        {
            if (Index < Count - 1)
            {
                var CurSectInfo  = this.SectionsInfo.Get_SectPr(Index);
                var NextSectInfo = this.SectionsInfo.Get_SectPr(Index + 1);
                if (CurSectInfo !== NextSectInfo)
                {
                    PageColumn.EndPos  = Index;
                    PageSection.EndPos = Index;
                    Page.EndPos        = Index;

                    if (c_oAscSectionBreakType.Continuous === NextSectInfo.SectPr.Get_Type() && true === CurSectInfo.SectPr.Compare_PageSize(NextSectInfo.SectPr) && this.Footnotes.IsEmptyPage(PageIndex))
                    {
                        // Новая секция начинается на данной странице. Нам надо получить новые поля данной секции, но
                        // на данной странице мы будет использовать только новые горизонтальные поля, а поля по вертикали
                        // используем от предыдущей секции.

                        var SectionY = Y;
                        for (var TempColumnIndex = 0; TempColumnIndex < ColumnsCount; ++TempColumnIndex)
                        {
                            if (PageSection.Columns[TempColumnIndex].Bounds.Bottom > SectionY)
                                SectionY = PageSection.Columns[TempColumnIndex].Bounds.Bottom;
                        }

                        var RealYLimit     = PageSection.YLimit;
                        PageSection.YLimit = SectionY;

                        if (true !== PageSection.Is_CalculatingSectionBottomLine() && ColumnsCount > 1 && true === PageSection.Can_RecalculateBottomLine())
                        {
                            PageSection.YLimit2 = RealYLimit;
                            PageSection.Calculate_BottomLine(false);

                            bContinue           = true;
                            _PageIndex          = PageIndex;
                            _SectionIndex       = SectionIndex;
                            _ColumnIndex        = 0;
                            _StartIndex         = this.Pages[_PageIndex].Sections[_SectionIndex].Columns[0].Pos;
                            _bStart             = false;
                            _bResetStartElement = 0 === SectionIndex ? Page.ResetStartElement : true;

                            this.Pages[_PageIndex].Sections[_SectionIndex].Reset_Columns();

                            break;
                        }
                        else
                        {
                            bContinue           = true;
                            _PageIndex          = PageIndex;
                            _SectionIndex       = SectionIndex + 1;
                            _ColumnIndex        = 0;
                            _StartIndex         = Index + 1;
                            _bStart             = false;
                            _bResetStartElement = true;

                            var NewPageSection           = new CDocumentPageSection();
                            NewPageSection.Pos           = Index;
                            NewPageSection.EndPos        = Index;
                            NewPageSection.Y             = SectionY + 0.001;
                            NewPageSection.YLimit        = true === PageSection.Is_CalculatingSectionBottomLine() ? PageSection.YLimit2 : RealYLimit;
                            NewPageSection.ColumnsSep    = NextSectInfo.SectPr.Get_ColumnsSep();
                            Page.Sections[_SectionIndex] = NewPageSection;

                            var ColumnsCount = NextSectInfo.SectPr.Get_ColumnsCount();
                            for (var ColumnIndex = 0; ColumnIndex < ColumnsCount; ++ColumnIndex)
                            {
                                Page.Sections[_SectionIndex].Columns[ColumnIndex] = new CDocumentPageColumn();
                            }

                            break;
                        }
                    }
                    else
                    {
                        bContinue           = true;
                        _PageIndex          = PageIndex + 1;
                        _SectionIndex       = 0;
                        _ColumnIndex        = 0;
                        _StartIndex         = Index + 1;
                        _bStart             = true;
                        _bResetStartElement = true;
                        break;
                    }
                }
            }
        }
        else if (RecalcResult & recalcresult_NextPage)
        {
            if (true === PageSection.Is_CalculatingSectionBottomLine() && (RecalcResult & recalcresultflags_LastFromNewPage || ColumnIndex >= ColumnsCount - 1))
            {
                PageSection.Calculate_BottomLine(true);

                bContinue           = true;
                _PageIndex          = PageIndex;
                _SectionIndex       = SectionIndex;
                _ColumnIndex        = 0;
                _StartIndex         = this.Pages[_PageIndex].Sections[_SectionIndex].Columns[0].Pos;
                _bStart             = false;
                _bResetStartElement = 0 === SectionIndex ? Page.ResetStartElement : true;

                this.Pages[_PageIndex].Sections[_SectionIndex].Reset_Columns();

                bReDraw = false;
                break;
            }
            else if (RecalcResult & recalcresultflags_LastFromNewColumn)
            {
                PageColumn.EndPos  = Index - 1;
                PageSection.EndPos = Index - 1;
                Page.EndPos        = Index - 1;

                bContinue           = true;
                _SectionIndex       = SectionIndex;
                _ColumnIndex        = ColumnIndex + 1;
                _PageIndex          = PageIndex;
                _StartIndex         = Index;
                _bStart             = true;
                _bResetStartElement = true;

                if (_ColumnIndex >= ColumnsCount)
                {
                    _SectionIndex = 0;
                    _ColumnIndex  = 0;
                    _PageIndex    = PageIndex + 1;
                }
                else
                {
                    bReDraw = false;
                }

                break;
            }
            else if (RecalcResult & recalcresultflags_LastFromNewPage)
            {
                PageColumn.EndPos  = Index - 1;
                PageSection.EndPos = Index - 1;
                Page.EndPos        = Index - 1;

                bContinue = true;

                _SectionIndex       = 0;
                _ColumnIndex        = 0;
                _PageIndex          = PageIndex + 1;
                _StartIndex         = Index;
                _bStart             = true;
                _bResetStartElement = true;

                if (PageColumn.EndPos === PageColumn.Pos)
                {
                    var Element          = this.Content[PageColumn.Pos];
                    var ElementPageIndex = this.private_GetElementPageIndex(Index, PageIndex, ColumnIndex, ColumnsCount);
                    if (true === Element.Is_EmptyPage(ElementPageIndex))
                        PageColumn.Empty = true;
                }

                for (var TempColumnIndex = ColumnIndex + 1; TempColumnIndex < ColumnsCount; ++TempColumnIndex)
                {
                    PageSection.Columns[TempColumnIndex].Empty  = true;
                    PageSection.Columns[TempColumnIndex].Pos    = Index;
                    PageSection.Columns[TempColumnIndex].EndPos = Index - 1;
                }

                break;
            }
            else if (RecalcResult & recalcresultflags_Page)
            {
                PageColumn.EndPos  = Index;
                PageSection.EndPos = Index;
                Page.EndPos        = Index;

                bContinue = true;

                _SectionIndex = 0;
                _ColumnIndex  = 0;
                _PageIndex    = PageIndex + 1;
                _StartIndex   = Index;
                _bStart       = true;

                if (PageColumn.EndPos === PageColumn.Pos)
                {
                    var Element          = this.Content[PageColumn.Pos];
                    var ElementPageIndex = this.private_GetElementPageIndex(Index, PageIndex, ColumnIndex, ColumnsCount);
                    if (true === Element.Is_EmptyPage(ElementPageIndex))
                        PageColumn.Empty = true;
                }

                for (var TempColumnIndex = ColumnIndex + 1; TempColumnIndex < ColumnsCount; ++TempColumnIndex)
                {
                    var ElementPageIndex = this.private_GetElementPageIndex(Index, PageIndex, TempColumnIndex, ColumnsCount);
                    this.Content[Index].Recalculate_SkipPage(ElementPageIndex);

                    PageSection.Columns[TempColumnIndex].Empty  = true;
                    PageSection.Columns[TempColumnIndex].Pos    = Index;
                    PageSection.Columns[TempColumnIndex].EndPos = Index - 1;
                }

                break;
            }
            else
            {
                PageColumn.EndPos  = Index;
                PageSection.EndPos = Index;
                Page.EndPos        = Index;

                bContinue = true;

                _ColumnIndex = ColumnIndex + 1;
                if (_ColumnIndex >= ColumnsCount)
                {
                    _SectionIndex = 0;
                    _ColumnIndex  = 0;
                    _PageIndex    = PageIndex + 1;
                }
                else
                {
                    bReDraw = false;
                }

                _StartIndex = Index;
                _bStart     = true;

                if (PageColumn.EndPos === PageColumn.Pos)
                {
                    var Element          = this.Content[PageColumn.Pos];
                    var ElementPageIndex = this.private_GetElementPageIndex(Index, PageIndex, ColumnIndex, ColumnsCount);
                    if (true === Element.Is_EmptyPage(ElementPageIndex))
                        PageColumn.Empty = true;
                }

                break;
            }
        }
        else if (RecalcResult & recalcresult_PrevPage)
        {
            bReDraw   = false;
            bContinue = true;
            if (RecalcResult & recalcresultflags_Column)
            {
                if (0 === ColumnIndex)
                {
                    _PageIndex    = Math.max(PageIndex - 1, 0);
                    _SectionIndex = this.Pages[_PageIndex].Sections.length - 1;
                    _ColumnIndex  = this.Pages[_PageIndex].Sections[_SectionIndex].Columns.length - 1;
                }
                else
                {
                    _PageIndex    = PageIndex;
                    _ColumnIndex  = ColumnIndex - 1;
                    _SectionIndex = SectionIndex;
                }
            }
            else
            {
                if (_SectionIndex > 0)
                {
                    // Сюда мы никогда не должны попадать
                }

                _PageIndex    = Math.max(PageIndex - 1, 0);
                _SectionIndex = this.Pages[_PageIndex].Sections.length - 1;
                _ColumnIndex  = 0;
            }

            _StartIndex = this.Pages[_PageIndex].Sections[_SectionIndex].Columns[_ColumnIndex].Pos;
            _bStart     = false;
            break;
        }

        if (docpostype_Content == this.Get_DocPosType() && Index === this.CurPos.ContentPos)
        {
            if (type_Paragraph === Element.GetType())
                this.CurPage = PageIndex;
            else
                this.CurPage = PageIndex; // TODO: переделать
        }

        if (docpostype_Content === this.Get_DocPosType() && ((true !== this.Selection.Use && Index > this.CurPos.ContentPos) || (true === this.Selection.Use && Index > this.Selection.EndPos && Index > this.Selection.StartPos)))
            this.private_UpdateCursorXY(true, true);
    }

    if (Index >= Count)
    {
        // До перерисовки селекта должны выставить
        Page.EndPos        = Count - 1;
        PageSection.EndPos = Count - 1;
        PageColumn.EndPos  = Count - 1;

        //console.log("LastRecalc: " + ((new Date().getTime() - this.StartTime) / 1000));
    }

    if (Index >= Count || _PageIndex > PageIndex || _ColumnIndex > ColumnIndex)
    {
        this.private_RecalculateShiftFootnotes(PageIndex, ColumnIndex, Y, SectPr);
    }

    if (true === bReDraw)
    {
        this.DrawingDocument.OnRecalculatePage(PageIndex, this.Pages[PageIndex]);
    }

    if (Index >= Count)
    {
		// Пересчет основной части документа законечен. Возможна ситуация, при которой последние сноски с данной
		// страницы переносятся на следующую (т.е. остались непересчитанные сноски). Эти сноски нужно пересчитать
		if (this.Footnotes.HaveContinuesFootnotes(PageIndex, ColumnIndex))
		{
			bContinue    = true;
			_PageIndex   = PageIndex;
			_ColumnIndex = ColumnIndex + 1;
			if (_ColumnIndex >= ColumnsCount)
			{
				_ColumnIndex = 0;
				_PageIndex   = PageIndex + 1;
			}

			_bStart     = true;
			_StartIndex = Count;
		}
		else
		{
			this.private_CheckUnusedFields();
			this.private_CheckCurPage();
			this.DrawingDocument.OnEndRecalculate(true);
			this.DrawingObjects.onEndRecalculateDocument(this.Pages.length);

			if (true === this.Selection.UpdateOnRecalc)
			{
				this.Selection.UpdateOnRecalc = false;
				this.DrawingDocument.OnSelectEnd();
			}

			this.FullRecalc.Id           = null;
			this.FullRecalc.MainStartPos = -1;

			// Основной пересчет окончен, если в колонтитулах есть элемент с количеством страниц, тогда нам надо
			// запустить дополнительный пересчет колонтитулов.
			// Если так случилось, что после повторного полного пересчета, вызванного изменением количества страниц и
			// изменением метрик колонтитула, новое количество страниц стало меньше, чем раньше, тогда мы не пересчитываем
			// дальше, чтобы избежать зацикливаний.

			if (-1 === this.HdrFtrRecalc.PageCount || this.HdrFtrRecalc.PageCount < this.Pages.length)
			{
				this.HdrFtrRecalc.PageCount = this.Pages.length;
				var nPageCountStartPage     = this.HdrFtr.HavePageCountElement();
				if (-1 !== nPageCountStartPage)
				{
					this.DrawingDocument.OnStartRecalculate(nPageCountStartPage);
					this.HdrFtrRecalc.PageIndex = nPageCountStartPage;
					this.private_RecalculateHdrFtrPageCountUpdate();
				}
			}

			//TODO функция не должна вызываться здесь! необходимо перенести(DrawingDocument.UpdateTarget)
			var clipboardBase = window['AscCommon'].g_clipboardBase;
			if(clipboardBase && clipboardBase.showButtonIdParagraph && !clipboardBase.pasteStart && clipboardBase.showSpecialPasteButton)
			{
				window['AscCommon'].g_clipboardBase.SpecialPasteButtonById_Show();
			}
			window['AscCommon'].g_clipboardBase.endRecalcDocument = true;
		}
    }

    if (true === bContinue)
    {
        this.FullRecalc.PageIndex         = _PageIndex;
        this.FullRecalc.SectionIndex      = _SectionIndex;
        this.FullRecalc.ColumnIndex       = _ColumnIndex;
        this.FullRecalc.StartIndex        = _StartIndex;
        this.FullRecalc.Start             = _bStart;
        this.FullRecalc.ResetStartElement = _bResetStartElement;
        this.FullRecalc.MainStartPos      = _StartIndex;

        if (window["NATIVE_EDITOR_ENJINE_SYNC_RECALC"] === true)
        {
            if (_PageIndex > this.FullRecalc.StartPage + 2)
            {
                if (window["native"]["WC_CheckSuspendRecalculate"] !== undefined)
                {
                    //if (window["native"]["WC_CheckSuspendRecalculate"]())
                    //    return;

                    this.FullRecalc.Id = setTimeout(Document_Recalculate_Page, 10);
                    return;
                }
            }

            this.Recalculate_Page();
            return;
        }

        if (_PageIndex > this.FullRecalc.StartPage + 2)
        {
            this.FullRecalc.Id = setTimeout(Document_Recalculate_Page, 20);
        }
        else
        {
            this.Recalculate_Page();
        }
    }
};
CDocument.prototype.private_RecalculateIsNewSection = function(nPageAbs, nContentIndex)
{
	// Определим, является ли данная страница первой в новой секции
	var bNewSection = ( 0 === nPageAbs ? true : false );
	if (0 !== nPageAbs)
	{
		var PrevStartIndex = this.Pages[nPageAbs - 1].Pos;
		var CurSectInfo    = this.SectionsInfo.Get_SectPr(nContentIndex);
		var PrevSectInfo   = this.SectionsInfo.Get_SectPr(PrevStartIndex);

		if (PrevSectInfo !== CurSectInfo && (c_oAscSectionBreakType.Continuous !== CurSectInfo.SectPr.Get_Type() || true !== CurSectInfo.SectPr.Compare_PageSize(PrevSectInfo.SectPr) ))
			bNewSection = true;
	}

	return bNewSection;
};
CDocument.prototype.private_RecalculateShiftFootnotes = function(nPageAbs, nColumnAbs, dY, oSectPr)
{
	var nPosType = oSectPr.GetFootnotePos();

	// section_footnote_PosDocEnd, section_footnote_PosSectEnd ненужные константы по логике, но Word воспринимает их
	// именно как section_footnote_PosBeneathText, в то время как все остальное (даже константа не по формату)
	// воспринимает как  section_footnote_PosPageBottom.
	if (section_footnote_PosBeneathText === nPosType || section_footnote_PosDocEnd === nPosType || section_footnote_PosSectEnd === nPosType)
	{
		this.Footnotes.Shift(nPageAbs, nColumnAbs, 0, dY);
	}
	else
	{
		var dFootnotesHeight = this.Footnotes.GetHeight(nPageAbs, nColumnAbs);
		var oPageMetrics     = this.Get_PageContentStartPos(nPageAbs);
		this.Footnotes.Shift(nPageAbs, nColumnAbs, 0, oPageMetrics.YLimit - dFootnotesHeight);
	}
};
CDocument.prototype.private_RecalculateFlowTable             = function(RecalcInfo)
{
    var Element            = RecalcInfo.Element;
    var X                  = RecalcInfo.X;
    var Y                  = RecalcInfo.Y;
    var XLimit             = RecalcInfo.XLimit;
    var YLimit             = RecalcInfo.YLimit;
    var PageIndex          = RecalcInfo.PageIndex;
    var ColumnIndex        = RecalcInfo.ColumnIndex;
    var Index              = RecalcInfo.Index;
    var StartIndex         = RecalcInfo.StartIndex;
    var ColumnsCount       = RecalcInfo.ColumnsCount;
    var bResetStartElement = RecalcInfo.ResetStartElement;
    var RecalcResult       = RecalcInfo.RecalcResult;

    // Когда у нас колонки мы не разбиваем плавающую таблицу на страницы.
    var isColumns = ColumnsCount > 1 ? true : false;
    if (true === isColumns)
        YLimit = 10000;

    if (true === this.RecalcInfo.Can_RecalcObject())
    {
        var ElementPageIndex = 0;
        if ((0 === Index && 0 === PageIndex) || Index != StartIndex || (Index === StartIndex && true === bResetStartElement))
        {
            Element.Set_DocumentIndex(Index);
            Element.Reset(X, Y, XLimit, YLimit, PageIndex, ColumnIndex, ColumnsCount);
            ElementPageIndex = 0;
        }
        else
        {
            ElementPageIndex = PageIndex - Element.PageNum;
        }

        var TempRecalcResult = Element.Recalculate_Page(ElementPageIndex);
        this.RecalcInfo.Set_FlowObject(Element, ElementPageIndex, TempRecalcResult, -1, {
            X      : X,
            Y      : Y,
            XLimit : XLimit,
            YLimit : YLimit
        });

        if (((0 === Index && 0 === PageIndex) || Index != StartIndex) && true != Element.IsContentOnFirstPage() && true !== isColumns)
        {
            this.RecalcInfo.Set_PageBreakBefore(true);
            RecalcResult = recalcresult_NextPage | recalcresultflags_LastFromNewPage;
        }
        else
        {
            var FlowTable = new CFlowTable(Element, PageIndex);
            this.DrawingObjects.addFloatTable(FlowTable);
            RecalcResult = recalcresult_CurPage;
        }
    }
    else if (true === this.RecalcInfo.Check_FlowObject(Element))
    {
        if (Element.PageNum === PageIndex)
        {
            if (true === this.RecalcInfo.Is_PageBreakBefore())
            {
                this.RecalcInfo.Reset();
                RecalcResult = recalcresult_NextPage | recalcresultflags_LastFromNewPage;
            }
            else
            {
                X      = this.RecalcInfo.AdditionalInfo.X;
                Y      = this.RecalcInfo.AdditionalInfo.Y;
                XLimit = this.RecalcInfo.AdditionalInfo.XLimit;
                YLimit = this.RecalcInfo.AdditionalInfo.YLimit;

                // Пересчет нужнен для обновления номеров колонок и страниц
                Element.Reset(X, Y, XLimit, YLimit, PageIndex, ColumnIndex, ColumnsCount);
                RecalcResult = Element.Recalculate_Page(0);
                this.RecalcInfo.FlowObjectPage++;

                if (true === isColumns)
                    RecalcResult = recalcresult_NextElement;

                if (RecalcResult & recalcresult_NextElement)
                    this.RecalcInfo.Reset();
            }
        }
        else if (Element.PageNum > PageIndex || (this.RecalcInfo.FlowObjectPage <= 0 && Element.PageNum < PageIndex))
        {
            this.DrawingObjects.removeFloatTableById(PageIndex - 1, Element.Get_Id());
            this.RecalcInfo.Set_PageBreakBefore(true);
            RecalcResult = recalcresult_PrevPage;
        }
        else
        {
            RecalcResult = Element.Recalculate_Page(PageIndex - Element.PageNum);
            this.RecalcInfo.FlowObjectPage++;
            this.DrawingObjects.addFloatTable(new CFlowTable(Element, PageIndex));

            if (RecalcResult & recalcresult_NextElement)
                this.RecalcInfo.Reset();
        }
    }
    else
    {
        RecalcResult = recalcresult_NextElement;
    }

    RecalcInfo.Index        = Index;
    RecalcInfo.RecalcResult = RecalcResult;
};
CDocument.prototype.private_RecalculateFlowParagraph         = function(RecalcInfo)
{
    var Element            = RecalcInfo.Element;
    var X                  = RecalcInfo.X;
    var Y                  = RecalcInfo.Y;
    var XLimit             = RecalcInfo.XLimit;
    var YLimit             = RecalcInfo.YLimit;
    var PageIndex          = RecalcInfo.PageIndex;
    var ColumnIndex        = RecalcInfo.ColumnIndex;
    var Index              = RecalcInfo.Index;
    var StartIndex         = RecalcInfo.StartIndex;
    var ColumnsCount       = RecalcInfo.ColumnsCount;
    var bResetStartElement = RecalcInfo.ResetStartElement;
    var RecalcResult       = RecalcInfo.RecalcResult;

    var Page = this.Pages[PageIndex];

    if (true === this.RecalcInfo.Can_RecalcObject())
    {
        var FramePr = Element.Get_FramePr();

        // Рассчитаем количество подряд идущих параграфов с одинаковыми FramePr
        var FlowCount = this.private_RecalculateFlowParagraphCount(Index);

        var Page_W = Page.Width;
        var Page_H = Page.Height;

        var Page_Field_L = Page.Margins.Left;
        var Page_Field_R = Page.Margins.Right;
        var Page_Field_T = Page.Margins.Top;
        var Page_Field_B = Page.Margins.Bottom;

        var Column_Field_L = X;
        var Column_Field_R = XLimit;

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

        for (var TempIndex = Index; TempIndex < Index + FlowCount; ++TempIndex)
        {
            var TempElement = this.Content[TempIndex];
            TempElement.Set_DocumentIndex(TempIndex);

			var ElementPageIndex = 0;
			if ((0 === TempIndex && 0 === PageIndex) || TempIndex != StartIndex || (TempIndex === StartIndex && true === bResetStartElement))
			{
				TempElement.Set_DocumentIndex(TempIndex);
				TempElement.Reset(0, FrameH, Frame_XLimit, Frame_YLimit, PageIndex, ColumnIndex, ColumnsCount);
				ElementPageIndex = 0;
			}
			else
			{
				ElementPageIndex = PageIndex - Element.PageNum;
			}

            RecalcResult = TempElement.Recalculate_Page(ElementPageIndex);

            if (!(RecalcResult & recalcresult_NextElement))
                break;

            FrameH = TempElement.Get_PageBounds(0).Bottom;
        }

        if (-1 === FrameW && 1 === FlowCount && 1 === Element.Lines.length && undefined === FramePr.Get_W())
        {
			FrameW     = Element.GetAutoWidthForDropCap();
			var ParaPr = Element.Get_CompiledPr2(false).ParaPr;
			FrameW += ParaPr.Ind.Left + ParaPr.Ind.FirstLine;

            // Если прилегание в данном случае не к левой стороне, тогда пересчитываем параграф,
            // с учетом того, что ширина буквицы должна быть FrameW
            if (align_Left != ParaPr.Jc)
            {
                Element.Reset(0, 0, FrameW, Frame_YLimit, PageIndex, ColumnIndex, ColumnsCount);
                Element.Recalculate_Page(0);
                FrameH = TempElement.Get_PageBounds(0).Bottom;
            }
        }
        else if (-1 === FrameW)
        {
            FrameW = Frame_XLimit;
        }

        var FrameHRule = ( undefined === FramePr.HRule ? Asc.linerule_Auto : FramePr.HRule );
        if ((Asc.linerule_AtLeast === FrameHRule && FrameH < FramePr.H) || Asc.linerule_Exact === FrameHRule)
        {
            FrameH = FramePr.H;
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
                            FrameX = Column_Field_L;
                            break;
                        case c_oAscXAlign.Right   :
                            FrameX = Column_Field_R - FrameW;
                            break;
                        case c_oAscXAlign.Center  :
                            FrameX = (Column_Field_R + Column_Field_L - FrameW) / 2;
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

        if (!(RecalcResult & recalcresult_NextElement))
        {
            // Ничего не делаем здесь, пересчитываем текущую страницу заново, либо предыдущую

            if (RecalcResult & recalcresult_PrevPage)
                this.RecalcInfo.Set_FrameRecalc(false);

            // TODO: Если мы заново пересчитываем текущую страницу, проверить надо ли обнулять параметр RecalcInfo.FrameRecalc
        }
        else if ((FrameY2 + FrameH2 > YLimit || Y > YLimit - 0.001) && Index != StartIndex)
        {
            this.RecalcInfo.Set_FrameRecalc(true);
            RecalcResult = recalcresult_NextPage | recalcresultflags_LastFromNewColumn;
        }
        else
        {
            this.RecalcInfo.Set_FrameRecalc(false);
            for (var TempIndex = Index; TempIndex < Index + FlowCount; ++TempIndex)
            {
                var TempElement = this.Content[TempIndex];
                TempElement.Shift(TempElement.Pages.length - 1, FrameX, FrameY);
                TempElement.Set_CalculatedFrame(FrameX, FrameY, FrameW, FrameH, FrameX2, FrameY2, FrameW2, FrameH2, PageIndex);
            }

            var FrameDx = ( undefined === FramePr.HSpace ? 0 : FramePr.HSpace );
            var FrameDy = ( undefined === FramePr.VSpace ? 0 : FramePr.VSpace );

            this.DrawingObjects.addFloatTable(new CFlowParagraph(Element, FrameX2, FrameY2, FrameW2, FrameH2, FrameDx, FrameDy, Index, FlowCount, FramePr.Wrap));

            Index += FlowCount - 1;

            if (FrameY >= Y && FrameX >= X - 0.001)
            {
                RecalcResult = recalcresult_NextElement;
            }
            else
            {
                this.RecalcInfo.Set_FlowObject(Element, PageIndex, recalcresult_NextElement, FlowCount);
                RecalcResult = recalcresult_CurPage | recalcresultflags_Page;
            }
        }
    }
    else if (true === this.RecalcInfo.Check_FlowObject(Element) && true === this.RecalcInfo.Is_PageBreakBefore())
    {
        this.RecalcInfo.Reset();
        this.RecalcInfo.Set_FrameRecalc(true);
        RecalcResult = recalcresult_NextPage | recalcresultflags_LastFromNewPage;
    }
    else if (true === this.RecalcInfo.Check_FlowObject(Element))
    {
        if (this.RecalcInfo.FlowObjectPage !== PageIndex)
        {
            // Номер страницы не такой же (должен быть +1), значит нам надо заново персесчитать предыдущую страницу
            // с условием, что данная рамка начнется с новой страницы
            this.RecalcInfo.Set_PageBreakBefore(true);
            this.DrawingObjects.removeFloatTableById(this.RecalcInfo.FlowObjectPage, Element.Get_Id());
            RecalcResult = recalcresult_PrevPage | recalcresultflags_Page;
        }
        else
        {
            // Все нормально рассчиталось

            // В случае колонок может так случится, что логическое место окажется в другой колонке, поэтому мы делаем
            // Reset для обновления логической позиции, но физическую позицию не меняем.
            var FlowCount = this.RecalcInfo.FlowObjectElementsCount;
            for (var TempIndex = Index; TempIndex < Index + FlowCount; ++TempIndex)
            {
                var TempElement = this.Content[TempIndex];
                TempElement.Reset(TempElement.X, TempElement.Y, TempElement.XLimit, TempElement.YLimit, TempElement.PageNum, ColumnIndex, ColumnsCount);
            }


            Index += this.RecalcInfo.FlowObjectElementsCount - 1;
            this.RecalcInfo.Reset();
            RecalcResult = recalcresult_NextElement;
        }
    }
    else
    {
        // В случае колонок может так случится, что логическое место окажется в другой колонке, поэтому мы делаем
        // Reset для обновления логической позиции, но физическую позицию не меняем.
        var FlowCount = this.private_RecalculateFlowParagraphCount(Index);
        for (var TempIndex = Index; TempIndex < Index + FlowCount; ++TempIndex)
        {
            var TempElement = this.Content[TempIndex];
            TempElement.Reset(TempElement.X, TempElement.Y, TempElement.XLimit, TempElement.YLimit, PageIndex, ColumnIndex, ColumnsCount);
        }

        RecalcResult = recalcresult_NextElement;
    }

    RecalcInfo.Index        = Index;
    RecalcInfo.RecalcResult = RecalcResult;
};
CDocument.prototype.private_RecalculateFlowParagraphCount    = function(Index)
{
    var Element   = this.Content[Index];
    var FramePr   = Element.Get_FramePr();
    var FlowCount = 1;
    for (var TempIndex = Index + 1, Count = this.Content.length; TempIndex < Count; ++TempIndex)
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

    return FlowCount;
};
CDocument.prototype.private_RecalculateHdrFtrPageCountUpdate = function()
{
	this.HdrFtrRecalc.Id = null;

	var nPageAbs    = this.HdrFtrRecalc.PageIndex;
	var nPagesCount = this.Pages.length;

	while (nPageAbs < nPagesCount)
	{
		var Result = this.HdrFtr.RecalculatePageCountUpdate(nPageAbs, nPagesCount);
		if (null === Result)
		{
			nPageAbs++;
		}
		else if (false === Result)
		{
			this.DrawingDocument.OnRecalculatePage(nPageAbs, this.Pages[nPageAbs]);

			if (nPageAbs < this.HdrFtrRecalc.PageIndex + 5)
			{
				nPageAbs++;
			}
			else
			{
				this.HdrFtrRecalc.PageIndex = nPageAbs + 1;
				this.HdrFtrRecalc.Id        = setTimeout(Document_Recalculate_HdrFtrPageCount, 20);
				return;
			}
		}
		else
		{
			this.RecalcInfo.Reset();
			this.FullRecalc.PageIndex         = nPageAbs;
			this.FullRecalc.SectionIndex      = 0;
			this.FullRecalc.ColumnIndex       = 0;
			this.FullRecalc.StartIndex        = this.Pages[nPageAbs].Pos;
			this.FullRecalc.Start             = true;
			this.FullRecalc.StartPage         = nPageAbs;
			this.FullRecalc.ResetStartElement = this.private_RecalculateIsNewSection(nPageAbs, this.Pages[nPageAbs].Pos);
			this.FullRecalc.MainStartPos      = this.Pages[nPageAbs].Pos;

			this.DrawingDocument.OnStartRecalculate(nPageAbs);
			this.Recalculate_Page();
			return;
		}
	}

	if (nPageAbs >= nPagesCount)
		this.DrawingDocument.OnEndRecalculate(false, true);
};
CDocument.prototype.private_CheckUnusedFields = function()
{
	if (this.Content.length <= 0)
		return;

	var oLastPara = this.Content[this.Content.length - 1];
	if (type_Paragraph !== oLastPara.GetType())
		return;

	var oInfo = oLastPara.GetEndInfoByPage(oLastPara.GetPagesCount() - 1);
	for (var nIndex = 0, nCount = oInfo.ComplexFields.length; nIndex < nCount; ++nIndex)
	{
		var oComplexField = oInfo.ComplexFields[nIndex].ComplexField;
		var oBeginChar    = oComplexField.GetBeginChar();
		var oEndChar      = oComplexField.GetEndChar();
		var oSeparateChar = oComplexField.GetSeparateChar();

		if (oBeginChar)
			oBeginChar.SetUse(false);

		if (oEndChar)
			oEndChar.SetUse(false);

		if (oSeparateChar)
			oSeparateChar.SetUse(false);
	}
};
CDocument.prototype.OnColumnBreak_WhileRecalculate           = function()
{
    var PageIndex    = this.FullRecalc.PageIndex;
    var SectionIndex = this.FullRecalc.SectionIndex;

    if (this.Pages[PageIndex] && this.Pages[PageIndex].Sections[SectionIndex])
        this.Pages[PageIndex].Sections[SectionIndex].DoNotRecalc_BottomLine();
};
CDocument.prototype.Reset_RecalculateCache                   = function()
{
    this.SectionsInfo.Reset_HdrFtrRecalculateCache();

    var Count = this.Content.length;
    for (var Index = 0; Index < Count; Index++)
    {
        this.Content[Index].Reset_RecalculateCache();
    }

    this.Footnotes.ResetRecalculateCache();
};
CDocument.prototype.Stop_Recalculate                         = function()
{
    if (null != this.FullRecalc.Id)
    {
        clearTimeout(this.FullRecalc.Id);
        this.FullRecalc.Id = null;
    }

    this.DrawingDocument.OnStartRecalculate(0);
};
CDocument.prototype.OnContentRecalculate                     = function(bNeedRecalc, PageNum, DocumentIndex)
{
    if (false === bNeedRecalc)
    {
        var Element = this.Content[DocumentIndex];
        // Просто перерисуем все страницы, на которых находится данный элеменет
        for (var PageNum = Element.PageNum; PageNum < Element.PageNum + Element.Pages.length; PageNum++)
        {
            this.DrawingDocument.OnRecalculatePage(PageNum, this.Pages[PageNum]);
        }

        this.DrawingDocument.OnEndRecalculate(false, true);

        this.Document_UpdateRulersState();
    }
    else
    {
        this.Recalculate(false, false);
    }
};
CDocument.prototype.OnContentReDraw                          = function(StartPage, EndPage)
{
    this.ReDraw(StartPage, EndPage);
};
CDocument.prototype.CheckTargetUpdate = function()
{
	// Проверим можно ли вообще пересчитывать текущее положение.
	if (this.DrawingDocument.UpdateTargetFromPaint === true)
	{
		if (true === this.DrawingDocument.UpdateTargetCheck)
			this.NeedUpdateTarget = this.DrawingDocument.UpdateTargetCheck;
		this.DrawingDocument.UpdateTargetCheck = false;
	}

	var bFlag = this.Controller.CanUpdateTarget();

	if (true === this.NeedUpdateTarget && true === bFlag && false === this.IsMovingTableBorder())
	{
		// Обновляем курсор сначала, чтобы обновить текущую страницу
		this.RecalculateCurPos();
		this.NeedUpdateTarget = false;
	}
};
CDocument.prototype.RecalculateCurPos = function()
{
	if (true === this.TurnOffRecalcCurPos)
		return;

	if (true === AscCommon.CollaborativeEditing.Get_GlobalLockSelection())
		return;

	this.DrawingDocument.UpdateTargetTransform(null);

	this.Controller.RecalculateCurPos();

	// TODO: Здесь добавлено обновление линейки, чтобы обновлялись границы рамки при наборе текста, а также чтобы
	//       обновлялись поля колонтитулов при наборе текста.
	this.Document_UpdateRulersState();
};
CDocument.prototype.private_CheckCurPage = function()
{
	if (true === this.TurnOffRecalcCurPos)
		return;

	if (true === AscCommon.CollaborativeEditing.Get_GlobalLockSelection())
		return;

	var nCurPage = this.Controller.GetCurPage();
	if (-1 !== nCurPage)
		this.CurPage = nCurPage;
};
CDocument.prototype.Set_TargetPos = function(X, Y, PageNum)
{
	this.TargetPos.X       = X;
	this.TargetPos.Y       = Y;
	this.TargetPos.PageNum = PageNum;
};
/**
 * Запрос на перерисовку заданного отрезка страниц.
 * @param StartPage
 * @param EndPage
 */
CDocument.prototype.ReDraw                                   = function(StartPage, EndPage)
{
    if ("undefined" === typeof(StartPage))
        StartPage = 0;
    if ("undefined" === typeof(EndPage))
        EndPage = this.DrawingDocument.m_lCountCalculatePages;

    for (var CurPage = StartPage; CurPage <= EndPage; CurPage++)
        this.DrawingDocument.OnRepaintPage(CurPage);
};
CDocument.prototype.DrawPage                                 = function(nPageIndex, pGraphics)
{
    this.Draw(nPageIndex, pGraphics);
};
CDocument.prototype.CanDrawPage = function(nPageAbs)
{
	if (null !== this.FullRecalc.Id && nPageAbs >= this.FullRecalc.PageIndex - 1)
		return false;

	return true;
};
/**
 * Перерисовка заданной страницы документа.
 * @param nPageIndex
 * @param pGraphics
 */
CDocument.prototype.Draw                                     = function(nPageIndex, pGraphics)
{
    // TODO: Пока делаем обновление курсоров при каждой отрисовке. Необходимо поменять
    this.CollaborativeEditing.Update_ForeignCursorsPositions();
    //--------------------------------------------------------------------------------------------------------------

    this.Comments.Reset_Drawing(nPageIndex);

    // Определим секцию
    var Page_StartPos = this.Pages[nPageIndex].Pos;
    var SectPr        = this.SectionsInfo.Get_SectPr(Page_StartPos).SectPr;

    if (docpostype_HdrFtr !== this.CurPos.Type && !this.IsViewMode())
        pGraphics.Start_GlobalAlpha();

    // Рисуем границы вокруг страницы (если границы надо рисовать под текстом)
    if (section_borders_ZOrderBack === SectPr.Get_Borders_ZOrder())
        this.Draw_Borders(pGraphics, SectPr);

    this.HdrFtr.Draw(nPageIndex, pGraphics);

    // Рисуем содержимое документа на данной странице
    if (docpostype_HdrFtr === this.CurPos.Type)
        pGraphics.put_GlobalAlpha(true, 0.4);
    else if (!this.IsViewMode())
        pGraphics.End_GlobalAlpha();

    this.DrawingObjects.drawBehindDoc(nPageIndex, pGraphics);

    this.Footnotes.Draw(nPageIndex, pGraphics);

    var Page = this.Pages[nPageIndex];
    for (var SectionIndex = 0, SectionsCount = Page.Sections.length; SectionIndex < SectionsCount; ++SectionIndex)
    {
        var PageSection = Page.Sections[SectionIndex];
        for (var ColumnIndex = 0, ColumnsCount = PageSection.Columns.length; ColumnIndex < ColumnsCount; ++ColumnIndex)
        {
            var Column         = PageSection.Columns[ColumnIndex];
            var ColumnStartPos = Column.Pos;
            var ColumnEndPos   = Column.EndPos;

            if (true === PageSection.ColumnsSep && ColumnIndex > 0 && !Column.IsEmpty())
			{

				var SepX = (Column.X + PageSection.Columns[ColumnIndex - 1].XLimit) / 2;
				pGraphics.p_color(0, 0, 0, 255);
				pGraphics.drawVerLine(c_oAscLineDrawingRule.Left, SepX, PageSection.Y, PageSection.YLimit, 0.75 * g_dKoef_pt_to_mm);
			}

            // Плавающие объекты не должны попадать в клип колонок
            var FlowElements = [];

            if (ColumnsCount > 1)
            {
                pGraphics.SaveGrState();

                var X    = ColumnIndex === 0 ? 0 : Column.X - Column.SpaceBefore / 2;
                var XEnd = (ColumnIndex >= ColumnsCount - 1 ? Page.Width : Column.XLimit + Column.SpaceAfter / 2);
                pGraphics.AddClipRect(X, 0, XEnd - X, Page.Height);
            }

            for (var ContentPos = ColumnStartPos; ContentPos <= ColumnEndPos; ++ContentPos)
            {
                if (true === this.Content[ContentPos].Is_Inline())
                {
                    var ElementPageIndex = this.private_GetElementPageIndex(ContentPos, nPageIndex, ColumnIndex, ColumnsCount);
                    this.Content[ContentPos].Draw(ElementPageIndex, pGraphics);
                }
                else
                {
                    FlowElements.push(ContentPos);
                }
            }

            if (ColumnsCount > 1)
            {
                pGraphics.RestoreGrState();
            }

            for (var FlowPos = 0, FlowsCount = FlowElements.length; FlowPos < FlowsCount; ++FlowPos)
            {
                var ContentPos       = FlowElements[FlowPos];
                var ElementPageIndex = this.private_GetElementPageIndex(ContentPos, nPageIndex, ColumnIndex, ColumnsCount);
                this.Content[ContentPos].Draw(ElementPageIndex, pGraphics);
            }
        }
    }

    this.DrawingObjects.drawWrappingObjects(nPageIndex, pGraphics);
    this.DrawingObjects.drawBeforeObjects(nPageIndex, pGraphics);

    // Рисуем границы вокруг страницы (если границы надо рисовать перед текстом)
    if (section_borders_ZOrderFront === SectPr.Get_Borders_ZOrder())
        this.Draw_Borders(pGraphics, SectPr);

    if (docpostype_HdrFtr === this.CurPos.Type)
    {
        pGraphics.put_GlobalAlpha(false, 1.0);

        // Рисуем колонтитулы
        var SectIndex = this.SectionsInfo.Get_Index(Page_StartPos);
        var SectCount = this.SectionsInfo.Get_Count();

        var SectIndex = ( 1 === SectCount ? -1 : SectIndex );

        var Header = this.HdrFtr.Pages[nPageIndex].Header;
        var Footer = this.HdrFtr.Pages[nPageIndex].Footer;

        var RepH = ( null === Header || null !== SectPr.Get_HdrFtrInfo(Header) ? false : true );
        var RepF = ( null === Footer || null !== SectPr.Get_HdrFtrInfo(Footer) ? false : true );

        var HeaderInfo = undefined;
        if (null !== Header && undefined !== Header.RecalcInfo.PageNumInfo[nPageIndex])
        {
            var bFirst = Header.RecalcInfo.PageNumInfo[nPageIndex].bFirst;
            var bEven  = Header.RecalcInfo.PageNumInfo[nPageIndex].bEven;

            var HeaderSectPr = Header.RecalcInfo.SectPr[nPageIndex];

            if (undefined !== HeaderSectPr)
                bFirst = ( true === bFirst && true === HeaderSectPr.Get_TitlePage() ? true : false );

            HeaderInfo = {bFirst : bFirst, bEven : bEven};
        }

        var FooterInfo = undefined;
        if (null !== Footer && undefined !== Footer.RecalcInfo.PageNumInfo[nPageIndex])
        {
            var bFirst = Footer.RecalcInfo.PageNumInfo[nPageIndex].bFirst;
            var bEven  = Footer.RecalcInfo.PageNumInfo[nPageIndex].bEven;

            var FooterSectPr = Footer.RecalcInfo.SectPr[nPageIndex];

            if (undefined !== FooterSectPr)
                bFirst = ( true === bFirst && true === FooterSectPr.Get_TitlePage() ? true : false );

            FooterInfo = {bFirst : bFirst, bEven : bEven};
        }

        pGraphics.DrawHeaderEdit(this.Pages[nPageIndex].Y, this.HdrFtr.Lock.Get_Type(), SectIndex, RepH, HeaderInfo);
        pGraphics.DrawFooterEdit(this.Pages[nPageIndex].YLimit, this.HdrFtr.Lock.Get_Type(), SectIndex, RepF, FooterInfo);
    }
};
CDocument.prototype.Draw_Borders                             = function(Graphics, SectPr)
{
    var Orient = SectPr.Get_Orientation();
    var Offset = SectPr.Get_Borders_OffsetFrom();

    var LBorder = SectPr.Get_Borders_Left();
    var TBorder = SectPr.Get_Borders_Top();
    var RBorder = SectPr.Get_Borders_Right();
    var BBorder = SectPr.Get_Borders_Bottom();

    var W = SectPr.Get_PageWidth();
    var H = SectPr.Get_PageHeight();

    // Порядок отрисовки границ всегда одинаковый вне зависимости от цветы и толщины: сначала вертикальные,
    // потом горизонтальные поверх вертикальных

    if (section_borders_OffsetFromPage === Offset)
    {
        // Рисуем левую границу
        if (border_None !== LBorder.Value)
        {
            var X  = LBorder.Space + LBorder.Size / 2;
            var Y0 = ( border_None !== TBorder.Value ? TBorder.Space + TBorder.Size / 2 : 0 );
            var Y1 = ( border_None !== BBorder.Value ? H - BBorder.Space - BBorder.Size / 2 : H );

            Graphics.p_color(LBorder.Color.r, LBorder.Color.g, LBorder.Color.b, 255);
            Graphics.drawVerLine(c_oAscLineDrawingRule.Center, X, Y0, Y1, LBorder.Size);
        }

        // Рисуем правую границу
        if (border_None !== RBorder.Value)
        {
            var X  = W - RBorder.Space - RBorder.Size / 2;
            var Y0 = ( border_None !== TBorder.Value ? TBorder.Space + TBorder.Size / 2 : 0 );
            var Y1 = ( border_None !== BBorder.Value ? H - BBorder.Space - BBorder.Size / 2 : H );

            Graphics.p_color(RBorder.Color.r, RBorder.Color.g, RBorder.Color.b, 255);
            Graphics.drawVerLine(c_oAscLineDrawingRule.Center, X, Y0, Y1, RBorder.Size);
        }

        // Рисуем верхнюю границу
        if (border_None !== TBorder.Value)
        {
            var Y  = TBorder.Space;
            var X0 = ( border_None !== LBorder.Value ? LBorder.Space + LBorder.Size / 2 : 0 );
            var X1 = ( border_None !== RBorder.Value ? W - RBorder.Space - RBorder.Size / 2 : W );

            Graphics.p_color(TBorder.Color.r, TBorder.Color.g, TBorder.Color.b, 255);
            Graphics.drawHorLineExt(c_oAscLineDrawingRule.Top, Y, X0, X1, TBorder.Size, ( border_None !== LBorder.Value ? -LBorder.Size / 2 : 0 ), ( border_None !== RBorder.Value ? RBorder.Size / 2 : 0 ));
        }

        // Рисуем нижнюю границу
        if (border_None !== BBorder.Value)
        {
            var Y  = H - BBorder.Space;
            var X0 = ( border_None !== LBorder.Value ? LBorder.Space + LBorder.Size / 2 : 0 );
            var X1 = ( border_None !== RBorder.Value ? W - RBorder.Space - RBorder.Size / 2 : W );

            Graphics.p_color(BBorder.Color.r, BBorder.Color.g, BBorder.Color.b, 255);
            Graphics.drawHorLineExt(c_oAscLineDrawingRule.Bottom, Y, X0, X1, BBorder.Size, ( border_None !== LBorder.Value ? -LBorder.Size / 2 : 0 ), ( border_None !== RBorder.Value ? RBorder.Size / 2 : 0 ));
        }
    }
    else
    {
        var _X0 = SectPr.Get_PageMargin_Left();
        var _X1 = W - SectPr.Get_PageMargin_Right();
        var _Y0 = SectPr.Get_PageMargin_Top();
        var _Y1 = H - SectPr.Get_PageMargin_Bottom();

        // Рисуем левую границу
        if (border_None !== LBorder.Value)
        {
            var X  = _X0 - LBorder.Space;
            var Y0 = ( border_None !== TBorder.Value ? _Y0 - TBorder.Space - TBorder.Size / 2 : _Y0 );
            var Y1 = ( border_None !== BBorder.Value ? _Y1 + BBorder.Space + BBorder.Size / 2 : _Y1 );

            Graphics.p_color(LBorder.Color.r, LBorder.Color.g, LBorder.Color.b, 255);
            Graphics.drawVerLine(c_oAscLineDrawingRule.Right, X, Y0, Y1, LBorder.Size);
        }

        // Рисуем правую границу
        if (border_None !== RBorder.Value)
        {
            var X  = _X1 + RBorder.Space;
            var Y0 = ( border_None !== TBorder.Value ? _Y0 - TBorder.Space - TBorder.Size / 2 : _Y0 );
            var Y1 = ( border_None !== BBorder.Value ? _Y1 + BBorder.Space + BBorder.Size / 2 : _Y1 );

            Graphics.p_color(RBorder.Color.r, RBorder.Color.g, RBorder.Color.b, 255);
            Graphics.drawVerLine(c_oAscLineDrawingRule.Left, X, Y0, Y1, RBorder.Size);
        }

        // Рисуем верхнюю границу
        if (border_None !== TBorder.Value)
        {
            var Y  = _Y0 - TBorder.Space;
            var X0 = ( border_None !== LBorder.Value ? _X0 - LBorder.Space : _X0 );
            var X1 = ( border_None !== RBorder.Value ? _X1 + RBorder.Space : _X1 );

            Graphics.p_color(TBorder.Color.r, TBorder.Color.g, TBorder.Color.b, 255);
            Graphics.drawHorLineExt(c_oAscLineDrawingRule.Bottom, Y, X0, X1, TBorder.Size, ( border_None !== LBorder.Value ? -LBorder.Size : 0 ), ( border_None !== RBorder.Value ? RBorder.Size : 0 ));
        }

        // Рисуем нижнюю границу
        if (border_None !== BBorder.Value)
        {
            var Y  = _Y1 + BBorder.Space;
            var X0 = ( border_None !== LBorder.Value ? _X0 - LBorder.Space : _X0 );
            var X1 = ( border_None !== RBorder.Value ? _X1 + RBorder.Space : _X1 );

            Graphics.p_color(BBorder.Color.r, BBorder.Color.g, BBorder.Color.b, 255);
            Graphics.drawHorLineExt(c_oAscLineDrawingRule.Top, Y, X0, X1, BBorder.Size, ( border_None !== LBorder.Value ? -LBorder.Size : 0 ), ( border_None !== RBorder.Value ? RBorder.Size : 0 ));
        }
    }

    // TODO: Реализовать:
    //       1. ArtBorders
    //       2. Различные типы обычных границ. Причем, если пересакающиеся границы имеют одинаковый тип и размер,
    //          тогда надо специально отрисовывать места соединения данных линий.

};
/**
 *
 * @param bRecalculate
 * @param bForceAdd - добавляем параграф, пропуская всякие проверки типа пустого параграфа с нумерацией.
 */
CDocument.prototype.AddNewParagraph = function(bRecalculate, bForceAdd)
{
	this.Controller.AddNewParagraph(bRecalculate, bForceAdd);
	this.Recalculate();
};
/**
 * Расширяем документ до точки (X,Y) с помощью новых параграфов.
 * Y0 - низ последнего параграфа, YLimit - предел страницы.
 * @param X
 * @param Y
 */
CDocument.prototype.Extend_ToPos = function(X, Y)
{
    var LastPara  = this.Content[this.Content.length - 1];
    var LastPara2 = LastPara;

    this.Create_NewHistoryPoint(AscDFH.historydescription_Document_DocumentExtendToPos);
    this.History.Set_Additional_ExtendDocumentToPos();

    while (true)
    {
        var NewParagraph = new Paragraph(this.DrawingDocument, this);
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
        if (NextId === this.Styles.Get_Default_Paragraph() || NextId === this.Styles.Get_Default_ParaList())
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
        var RecalcResult = NewParagraph.Recalculate_Page(0);

        if (recalcresult_NextElement != RecalcResult)
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

    if (LastPara != LastPara2 || false === this.Document_Is_SelectionLocked(changestype_None, {
            Type      : changestype_2_Element_and_Type,
            Element   : LastPara,
            CheckType : changestype_Paragraph_Content
        }))
    {
        // Теперь нам нужно вставить таб по X
        LastPara.Extend_ToPos(X);
    }

    LastPara.MoveCursorToEndPos();
    LastPara.Document_SetThisElementCurrent(true);

    this.Recalculate();
};
CDocument.prototype.GroupGraphicObjects = function()
{
	if (this.CanGroup())
	{
		this.DrawingObjects.groupSelectedObjects();
	}
};
CDocument.prototype.UnGroupGraphicObjects = function()
{
	if (this.CanUnGroup())
	{
		this.DrawingObjects.unGroupSelectedObjects();
	}
};
CDocument.prototype.StartChangeWrapPolygon = function()
{
	this.DrawingObjects.startChangeWrapPolygon();
};
CDocument.prototype.CanChangeWrapPolygon = function()
{
	return this.DrawingObjects.canChangeWrapPolygon();
};
CDocument.prototype.CanGroup = function()
{
	return this.DrawingObjects.canGroup();
};
CDocument.prototype.CanUnGroup = function()
{
	return this.DrawingObjects.canUnGroup();
};
CDocument.prototype.AddInlineImage = function(W, H, Img, Chart, bFlow)
{
	if (undefined === bFlow)
		bFlow = false;

	this.Controller.AddInlineImage(W, H, Img, Chart, bFlow);
};

CDocument.prototype.AddImages = function(aImages){
    this.Controller.AddImages(aImages);
};

CDocument.prototype.AddOleObject  = function(W, H, nWidthPix, nHeightPix, Img, Data, sApplicationId)
{
	this.Controller.AddOleObject(W, H, nWidthPix, nHeightPix, Img, Data, sApplicationId);
};
CDocument.prototype.EditOleObject = function(oOleObject, sData, sImageUrl, nPixWidth, nPixHeight)
{
	oOleObject.setData(sData);
	var _blipFill           = new AscFormat.CBlipFill();
	_blipFill.RasterImageId = sImageUrl;
	oOleObject.setBlipFill(_blipFill);
	oOleObject.setPixSizes(nPixWidth, nPixHeight);
};
CDocument.prototype.AddTextArt = function(nStyle)
{
	this.Controller.AddTextArt(nStyle);
};

CDocument.prototype.AddSignatureLine = function(oSignatureDrawing){
    this.Controller.AddSignatureLine(oSignatureDrawing);
};

CDocument.prototype.EditChart = function(Chart)
{
	this.Controller.EditChart(Chart);
};
CDocument.prototype.GetChartObject = function(type)
{
	return this.DrawingObjects.getChartObject(type);
};
CDocument.prototype.AddInlineTable = function(Cols, Rows)
{
	if (Cols <= 0 || Rows <= 0)
		return;

	this.Controller.AddInlineTable(Cols, Rows);

	this.Recalculate();

	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
	this.Document_UpdateRulersState();
};
CDocument.prototype.AddDropCap = function(bInText)
{
	// Определим параграф, к которому мы будем добавлять буквицу
	var Pos = -1;

	if (false === this.Selection.Use && type_Paragraph === this.Content[this.CurPos.ContentPos].GetType())
		Pos = this.CurPos.ContentPos;
	else if (true === this.Selection.Use && this.Selection.StartPos <= this.Selection.EndPos && type_Paragraph === this.Content[this.Selection.StartPos].GetType())
		Pos = this.Selection.StartPos;
	else if (true === this.Selection.Use && this.Selection.StartPos > this.Selection.EndPos && type_Paragraph === this.Content[this.Selection.EndPos].GetType())
		Pos = this.Selection.EndPos;

	if (-1 === Pos)
		return;

	var OldParagraph = this.Content[Pos];

	if (OldParagraph.Lines.length <= 0)
		return;

	if (false === this.Document_Is_SelectionLocked(changestype_None, {
			Type      : changestype_2_Element_and_Type,
			Element   : OldParagraph,
			CheckType : changestype_Paragraph_Content
		}))
	{
		this.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddDropCap);

		var NewParagraph = new Paragraph(this.DrawingDocument, this);

		var TextPr = OldParagraph.Split_DropCap(NewParagraph);
		var Before = OldParagraph.Get_CompiledPr().ParaPr.Spacing.Before;
		var LineH  = OldParagraph.Lines[0].Bottom - OldParagraph.Lines[0].Top - Before;
		var LineTA = OldParagraph.Lines[0].Metrics.TextAscent2;
		var LineTD = OldParagraph.Lines[0].Metrics.TextDescent + OldParagraph.Lines[0].Metrics.LineGap;

		var FramePr = new CFramePr();
		FramePr.Init_Default_DropCap(bInText);
		NewParagraph.Set_FrameParaPr(OldParagraph);
		NewParagraph.Set_FramePr2(FramePr);
		NewParagraph.Update_DropCapByLines(TextPr, NewParagraph.Pr.FramePr.Lines, LineH, LineTA, LineTD, Before);

		this.Internal_Content_Add(Pos, NewParagraph);
		NewParagraph.MoveCursorToEndPos();

		this.RemoveSelection();
		this.CurPos.ContentPos = Pos;
		this.Set_DocPosType(docpostype_Content);

		this.Recalculate();
		this.Document_UpdateInterfaceState();
		this.Document_UpdateRulersState();
	}
};
CDocument.prototype.RemoveDropCap = function(bDropCap)
{
	var Pos = -1;

	if (false === this.Selection.Use && type_Paragraph === this.Content[this.CurPos.ContentPos].GetType())
		Pos = this.CurPos.ContentPos;
	else if (true === this.Selection.Use && this.Selection.StartPos <= this.Selection.EndPos && type_Paragraph === this.Content[this.Selection.StartPos].GetType())
		Pos = this.Selection.StartPos;
	else if (true === this.Selection.Use && this.Selection.StartPos > this.Selection.EndPos && type_Paragraph === this.Content[this.Selection.EndPos].GetType())
		Pos = this.Selection.EndPos;

	if (-1 === Pos)
		return;

	var Para    = this.Content[Pos];
	var FramePr = Para.Get_FramePr();

	// Возможно буквицой является предыдущий параграф
	if (undefined === FramePr && true === bDropCap)
	{
		var Prev = Para.Get_DocumentPrev();
		if (null != Prev && type_Paragraph === Prev.GetType())
		{
			var PrevFramePr = Prev.Get_FramePr();
			if (undefined != PrevFramePr && undefined != PrevFramePr.DropCap)
			{
				Para    = Prev;
				FramePr = PrevFramePr;
			}
			else
				return;
		}
		else
			return;
	}

	if (undefined === FramePr)
		return;

	var FrameParas = Para.Internal_Get_FrameParagraphs();

	if (false === bDropCap)
	{
		if (false === this.Document_Is_SelectionLocked(changestype_None, {
				Type      : changestype_2_ElementsArray_and_Type,
				Elements  : FrameParas,
				CheckType : changestype_Paragraph_Content
			}))
		{
			this.Create_NewHistoryPoint(AscDFH.historydescription_Document_RemoveDropCap);
			var Count = FrameParas.length;
			for (var Index = 0; Index < Count; Index++)
			{
				FrameParas[Index].Set_FramePr(undefined, true);
			}

			this.Recalculate();
			this.Document_UpdateInterfaceState();
			this.Document_UpdateRulersState();
		}
	}
	else
	{
		// Сначала найдем параграф, к которому относится буквица
		var Next = Para.Get_DocumentNext();
		var Last = Para;
		while (null != Next)
		{
			if (type_Paragraph != Next.GetType() || undefined === Next.Get_FramePr() || true != FramePr.Compare(Next.Get_FramePr()))
				break;

			Last = Next;
			Next = Next.Get_DocumentNext();
		}

		if (null != Next && type_Paragraph === Next.GetType())
		{
			FrameParas.push(Next);
			if (false === this.Document_Is_SelectionLocked(changestype_None, {
					Type      : changestype_2_ElementsArray_and_Type,
					Elements  : FrameParas,
					CheckType : changestype_Paragraph_Content
				}))
			{
				this.Create_NewHistoryPoint(AscDFH.historydescription_Document_RemoveDropCap);

				// Удалим ненужный элемент
				FrameParas.splice(FrameParas.length - 1, 1);

				// Передвинем курсор в начало следующего параграфа, и рассчитаем текстовые настройки и расстояния между строк
				Next.MoveCursorToStartPos();
				var Spacing = Next.Get_CompiledPr2(false).ParaPr.Spacing.Copy();
				var TextPr  = Next.Get_FirstRunPr();

				var Count = FrameParas.length;
				for (var Index = 0; Index < Count; Index++)
				{
					var FramePara = FrameParas[Index];
					FramePara.Set_FramePr(undefined, true);
					FramePara.Set_Spacing(Spacing, true);
					FramePara.SelectAll();
					FramePara.Clear_TextFormatting();
					FramePara.Apply_TextPr(TextPr, undefined);
				}


				Next.CopyPr(Last);
				Last.Concat(Next);

				this.Internal_Content_Remove(Next.Index, 1);

				Last.MoveCursorToStartPos();
				Last.Document_SetThisElementCurrent(true);

				this.Recalculate();
				this.Document_UpdateInterfaceState();
				this.Document_UpdateRulersState();
			}
		}
		else
		{
			if (false === this.Document_Is_SelectionLocked(changestype_None, {
					Type      : changestype_2_ElementsArray_and_Type,
					Elements  : FrameParas,
					CheckType : changestype_Paragraph_Content
				}))
			{
				this.Create_NewHistoryPoint(AscDFH.historydescription_Document_RemoveDropCap);
				var Count = FrameParas.length;
				for (var Index = 0; Index < Count; Index++)
				{
					FrameParas[Index].Set_FramePr(undefined, true);
				}

				this.Recalculate();
				this.Document_UpdateInterfaceState();
				this.Document_UpdateRulersState();
			}
		}
	}
};
CDocument.prototype.private_CheckFramePrLastParagraph = function()
{
    var Count = this.Content.length;
    if (Count <= 0)
        return;

    var Element = this.Content[Count - 1];
    if (type_Paragraph === Element.GetType() && undefined !== Element.Get_FramePr())
    {
        Element.Set_FramePr(undefined, true);
    }
};
CDocument.prototype.CheckRange = function(X0, Y0, X1, Y1, _Y0, _Y1, X_lf, X_rf, PageNum, Inner, bMathWrap)
{
	var HdrFtrRanges = this.HdrFtr.CheckRange(X0, Y0, X1, Y1, _Y0, _Y1, X_lf, X_rf, PageNum, bMathWrap);
	return this.DrawingObjects.CheckRange(X0, Y0, X1, Y1, _Y0, _Y1, X_lf, X_rf, PageNum, HdrFtrRanges, null, bMathWrap);
};
CDocument.prototype.AddToParagraph = function(ParaItem, bRecalculate)
{
	this.Controller.AddToParagraph(ParaItem, bRecalculate);
};
CDocument.prototype.ClearParagraphFormatting  = function()
{
	this.Controller.ClearParagraphFormatting();

	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.Remove = function(nDirection, bOnlyText, bRemoveOnlySelection, bOnTextAdd)
{
	if (undefined === bRemoveOnlySelection)
		bRemoveOnlySelection = false;

	if (undefined === bOnTextAdd)
		bOnTextAdd = false;

	this.Controller.Remove(nDirection, bOnlyText, bRemoveOnlySelection, bOnTextAdd);

	this.Recalculate();

	this.Document_UpdateInterfaceState();
	this.Document_UpdateRulersState();
};
CDocument.prototype.RemoveBeforePaste = function()
{
	if (docpostype_DrawingObjects === this.Get_DocPosType() && null === this.DrawingObjects.getTargetDocContent())
		this.RemoveSelection();
	else
		this.Remove(1, true, true, true);
};
CDocument.prototype.GetCursorPosXY = function()
{
	return this.Controller.GetCursorPosXY();
};
CDocument.prototype.MoveCursorToStartPos = function(AddToSelect)
{
	this.Reset_WordSelection();
	this.private_UpdateTargetForCollaboration();

	this.Controller.MoveCursorToStartPos(AddToSelect);

	this.private_UpdateCursorXY(true, true);
};
CDocument.prototype.MoveCursorToEndPos = function(AddToSelect)
{
	this.Reset_WordSelection();
	this.private_UpdateTargetForCollaboration();

	this.Controller.MoveCursorToEndPos(AddToSelect);

	this.private_UpdateCursorXY(true, true);
};
CDocument.prototype.MoveCursorLeft = function(AddToSelect, Word)
{
	this.Reset_WordSelection();
	this.private_UpdateTargetForCollaboration();

	if (undefined === Word || null === Word)
		Word = false;

	this.Controller.MoveCursorLeft(AddToSelect, Word);

	this.Document_UpdateInterfaceState();
	this.Document_UpdateRulersState();
	this.private_UpdateCursorXY(true, true);
};
CDocument.prototype.MoveCursorRight = function(AddToSelect, Word, FromPaste)
{
	this.Reset_WordSelection();
	this.private_UpdateTargetForCollaboration();

	if (undefined === Word || null === Word)
		Word = false;

	this.Controller.MoveCursorRight(AddToSelect, Word, FromPaste);

	this.Document_UpdateInterfaceState();
	this.Document_UpdateSelectionState();
	this.private_UpdateCursorXY(true, true);
};
CDocument.prototype.MoveCursorUp = function(AddToSelect, CtrlKey)
{
	this.Reset_WordSelection();
	this.private_UpdateTargetForCollaboration();

	if (true === this.IsFillingFormMode())
		this.MoveToFillingForm(false);
	else
		this.Controller.MoveCursorUp(AddToSelect, CtrlKey);
};
CDocument.prototype.MoveCursorDown = function(AddToSelect, CtrlKey)
{
	this.Reset_WordSelection();
	this.private_UpdateTargetForCollaboration();

	if (true === this.IsFillingFormMode())
		this.MoveToFillingForm(true);
	else
		this.Controller.MoveCursorDown(AddToSelect, CtrlKey);
};
CDocument.prototype.MoveCursorToEndOfLine = function(AddToSelect)
{
	this.Reset_WordSelection();
	this.private_UpdateTargetForCollaboration();

	this.Controller.MoveCursorToEndOfLine(AddToSelect);

	this.Document_UpdateInterfaceState();
	this.private_UpdateCursorXY(true, true);
};
CDocument.prototype.MoveCursorToStartOfLine = function(AddToSelect)
{
	this.Reset_WordSelection();
	this.private_UpdateTargetForCollaboration();

	this.Controller.MoveCursorToStartOfLine(AddToSelect);

	this.Document_UpdateInterfaceState();
	this.private_UpdateCursorXY(true, true);
};
CDocument.prototype.MoveCursorToXY = function(X, Y, AddToSelect)
{
	this.Reset_WordSelection();
	this.private_UpdateTargetForCollaboration();
	this.Controller.MoveCursorToXY(X, Y, this.CurPage, AddToSelect);
};
CDocument.prototype.MoveCursorToCell = function(bNext)
{
	this.Reset_WordSelection();
	this.private_UpdateTargetForCollaboration();
	this.Controller.MoveCursorToCell(bNext);
};
CDocument.prototype.SetParagraphAlign = function(Align)
{
	var SelectedInfo = this.GetSelectedElementsInfo();
	var Math         = SelectedInfo.Get_Math();
	if (null !== Math && true !== Math.Is_Inline())
	{
		Math.Set_Align(Align);
	}
	else
	{
		this.Controller.SetParagraphAlign(Align);
	}

	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.SetParagraphSpacing = function(Spacing)
{
	this.Controller.SetParagraphSpacing(Spacing);
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.SetParagraphTabs = function(Tabs)
{
	this.Controller.SetParagraphTabs(Tabs);
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
	this.Api.Update_ParaTab(AscCommonWord.Default_Tab_Stop, Tabs);
};
CDocument.prototype.SetParagraphIndent = function(Ind)
{
	this.Controller.SetParagraphIndent(Ind);
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.SetParagraphNumbering = function(NumInfo)
{
	this.Controller.SetParagraphNumbering(NumInfo);
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.SetParagraphShd = function(Shd)
{
	this.Controller.SetParagraphShd(Shd);
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.SetParagraphStyle = function(Name)
{
	this.Controller.SetParagraphStyle(Name);
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.SetParagraphContextualSpacing = function(Value)
{
	this.Controller.SetParagraphContextualSpacing(Value);
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.SetParagraphPageBreakBefore = function(Value)
{
	this.Controller.SetParagraphPageBreakBefore(Value);
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.SetParagraphKeepLines = function(Value)
{
	this.Controller.SetParagraphKeepLines(Value);
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.SetParagraphKeepNext = function(Value)
{
	this.Controller.SetParagraphKeepNext(Value);
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.SetParagraphWidowControl = function(Value)
{
	this.Controller.SetParagraphWidowControl(Value);
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.SetParagraphBorders = function(Borders)
{
	this.Controller.SetParagraphBorders(Borders);
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.SetParagraphFramePr = function(FramePr, bDelete)
{
	this.Controller.SetParagraphFramePr(FramePr, bDelete);
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateRulersState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.IncreaseDecreaseFontSize = function(bIncrease)
{
	this.Controller.IncreaseDecreaseFontSize(bIncrease);
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.IncreaseDecreaseIndent = function(bIncrease)
{
	this.Controller.IncreaseDecreaseIndent(bIncrease);
};
CDocument.prototype.Paragraph_SetHighlight = function(IsColor, r, g, b)
{
	if (true === this.IsTextSelectionUse())
	{
		if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextHighlight);

			if (false === IsColor)
				this.AddToParagraph(new ParaTextPr({HighLight : highlight_None}));
			else
				this.AddToParagraph(new ParaTextPr({HighLight : new CDocumentColor(r, g, b)}));

			this.Document_UpdateInterfaceState();
			editor.sync_MarkerFormatCallback(false);
		}
	}
	else
	{
		if (false === IsColor)
			this.HighlightColor = highlight_None;
		else
			this.HighlightColor = new CDocumentColor(r, g, b);
	}
};
CDocument.prototype.SetImageProps = function(Props)
{
	this.Controller.SetImageProps(Props);
	this.Recalculate();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.ShapeApply = function(shapeProps)
{
	this.DrawingObjects.shapeApply(shapeProps);
};
CDocument.prototype.Select_Drawings = function(DrawingArray, TargetContent)
{
	this.private_UpdateTargetForCollaboration();

	if (DrawingArray.length === 1 && DrawingArray[0].Is_Inline())
		return;
	this.DrawingObjects.resetSelection();
	var hdr_ftr = TargetContent.Is_HdrFtr(true);
	if (hdr_ftr)
	{
		hdr_ftr.Content.Set_DocPosType(docpostype_DrawingObjects);
		hdr_ftr.Set_CurrentElement(false);
	}
	else
	{
		this.Set_DocPosType(docpostype_DrawingObjects);
	}
	for (var i = 0; i < DrawingArray.length; ++i)
	{
		this.DrawingObjects.selectObject(DrawingArray[i].GraphicObj, 0);
	}
};
CDocument.prototype.SetTableProps = function(Props)
{
	this.Controller.SetTableProps(Props);
	this.Recalculate();
	this.Document_UpdateInterfaceState();
	this.Document_UpdateRulersState();
	this.Document_UpdateSelectionState();
};
/**
 * Получаем рассчитанные настройки параграфа (полностью заполненные)
 * @returns {CParaPr}
 */
CDocument.prototype.GetCalculatedParaPr = function()
{
	return this.Controller.GetCalculatedParaPr();
};
/**
 * Получаем рассчитанные настройки текста (полностью заполненные)
 * @returns {CTextPr}
 */
CDocument.prototype.GetCalculatedTextPr = function()
{
	return this.Controller.GetCalculatedTextPr();
};
/**
 * Получаем прямые настройки параграфа, т.е. которые выставлены непосредственно у параграфа, без учета стилей
 * @returns {CParaPr}
 */
CDocument.prototype.GetDirectTextPr = function()
{
	return this.Controller.GetDirectTextPr();
};
/**
 * Получаем прямые настройки текста, т.е. которые выставлены непосредственно у рана, без учета стилей
 * @returns {CTextPr}
 */
CDocument.prototype.GetDirectParaPr = function()
{
	return this.Controller.GetDirectParaPr();
};
CDocument.prototype.Get_PageSizesByDrawingObjects = function()
{
	return this.DrawingObjects.getPageSizesByDrawingObjects();
};
CDocument.prototype.Set_DocumentMargin = function(MarPr)
{
	// TODO: Document.Set_DocumentOrientation Сделать в зависимости от выделения

	var CurPos = this.CurPos.ContentPos;
	var SectPr = this.SectionsInfo.Get_SectPr(CurPos).SectPr;

	var L = MarPr.Left;
	var T = MarPr.Top;
	var R = ( undefined === MarPr.Right ? undefined : SectPr.Get_PageWidth() - MarPr.Right );
	var B = ( undefined === MarPr.Bottom ? undefined : SectPr.Get_PageHeight() - MarPr.Bottom );

	SectPr.Set_PageMargins(L, T, R, B);
	this.DrawingObjects.CheckAutoFit();

	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
	this.Document_UpdateRulersState();
};
CDocument.prototype.Set_DocumentPageSize = function(W, H, bNoRecalc)
{
	// TODO: Document.Set_DocumentOrientation Сделать в зависимости от выделения

	var CurPos = this.CurPos.ContentPos;
	var SectPr = this.SectionsInfo.Get_SectPr(CurPos).SectPr;

	SectPr.Set_PageSize(W, H);

	this.DrawingObjects.CheckAutoFit();
	if (true != bNoRecalc)
	{
		this.Recalculate();
		this.Document_UpdateSelectionState();
		this.Document_UpdateInterfaceState();
		this.Document_UpdateRulersState();
	}
};
CDocument.prototype.Get_DocumentPageSize = function()
{
	// TODO: Document.Get_DocumentOrientation Сделать в зависимости от выделения

	var CurPos             = this.CurPos.ContentPos;
	var SectionInfoElement = this.SectionsInfo.Get_SectPr(CurPos);

	if (undefined === SectionInfoElement)
		return true;

	var SectPr = SectionInfoElement.SectPr;

	return {W : SectPr.Get_PageWidth(), H : SectPr.Get_PageHeight()};
};
CDocument.prototype.Set_DocumentOrientation = function(Orientation, bNoRecalc)
{
	// TODO: Document.Set_DocumentOrientation Сделать в зависимости от выделения

	var CurPos = this.CurPos.ContentPos;
	var SectPr = this.SectionsInfo.Get_SectPr(CurPos).SectPr;

	SectPr.Set_Orientation(Orientation, true);

	this.DrawingObjects.CheckAutoFit();
	if (true != bNoRecalc)
	{
		this.Recalculate();
		this.Document_UpdateSelectionState();
		this.Document_UpdateInterfaceState();
		this.Document_UpdateRulersState();
	}
};
CDocument.prototype.Get_DocumentOrientation = function()
{
	// TODO: Document.Get_DocumentOrientation Сделать в зависимости от выделения

	var CurPos             = this.CurPos.ContentPos;
	var SectionInfoElement = this.SectionsInfo.Get_SectPr(CurPos);

	if (undefined === SectionInfoElement)
		return true;

	var SectPr = SectionInfoElement.SectPr;

	return ( SectPr.Get_Orientation() === Asc.c_oAscPageOrientation.PagePortrait ? true : false );
};
CDocument.prototype.Set_DocumentDefaultTab = function(DTab)
{
	this.History.Add(new CChangesDocumentDefaultTab(this, AscCommonWord.Default_Tab_Stop, DTab));
	AscCommonWord.Default_Tab_Stop = DTab;
};
CDocument.prototype.Set_DocumentEvenAndOddHeaders = function(Value)
{
	if (Value !== EvenAndOddHeaders)
	{
		this.History.Add(new CChangesDocumentEvenAndOddHeaders(this, EvenAndOddHeaders, Value));
		EvenAndOddHeaders = Value;
	}
};
/**
 * Обновляем данные в интерфейсе о свойствах параграфа.
 */
CDocument.prototype.Interface_Update_ParaPr = function()
{
	if (!this.Api)
		return;

	var ParaPr = this.GetCalculatedParaPr();

	if (null != ParaPr)
	{
		// Проверим, можно ли добавить буквицу
		ParaPr.CanAddDropCap = false;

		if (docpostype_Content === this.Get_DocPosType())
		{
			var Para = null;
			if (false === this.Selection.Use && type_Paragraph === this.Content[this.CurPos.ContentPos].GetType())
				Para = this.Content[this.CurPos.ContentPos];
			else if (true === this.Selection.Use && this.Selection.StartPos <= this.Selection.EndPos && type_Paragraph === this.Content[this.Selection.StartPos].GetType())
				Para = this.Content[this.Selection.StartPos];
			else if (true === this.Selection.Use && this.Selection.StartPos > this.Selection.EndPos && type_Paragraph === this.Content[this.Selection.EndPos].GetType())
				Para = this.Content[this.Selection.EndPos];

			if (null != Para && undefined === Para.Get_FramePr())
			{
				var Prev = Para.Get_DocumentPrev();
				if ((null === Prev || type_Paragraph != Prev.GetType() || undefined === Prev.Get_FramePr() || undefined === Prev.Get_FramePr().DropCap) && true === Para.Can_AddDropCap())
					ParaPr.CanAddDropCap = true;
			}
		}

		var oSelectedInfo = this.GetSelectedElementsInfo();
		var Math          = oSelectedInfo.Get_Math();
		if (null !== Math)
			ParaPr.CanAddImage = false;
		else
			ParaPr.CanAddImage = true;

		if (undefined != ParaPr.Tabs)
			this.Api.Update_ParaTab(AscCommonWord.Default_Tab_Stop, ParaPr.Tabs);

		if (ParaPr.Shd && ParaPr.Shd.Unifill)
		{
			ParaPr.Shd.Unifill.check(this.theme, this.Get_ColorMap());
		}

		var SelectedInfo = this.GetSelectedElementsInfo();
		var Math         = SelectedInfo.Get_Math();
		if (null !== Math && true !== Math.Is_Inline())
			ParaPr.Jc = Math.Get_Align();

		this.Api.UpdateParagraphProp(ParaPr);
	}
};
/**
 * Обновляем данные в интерфейсе о свойствах текста.
 */
CDocument.prototype.Interface_Update_TextPr = function()
{
	if (!this.Api)
		return;

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
		if (TextPr.Unifill)
		{
			var RGBAColor = TextPr.Unifill.getRGBAColor();
			TextPr.Color  = new CDocumentColor(RGBAColor.R, RGBAColor.G, RGBAColor.B, false);
		}
		if (TextPr.Shd && TextPr.Shd.Unifill)
		{
			TextPr.Shd.Unifill.check(this.theme, this.Get_ColorMap());
		}
		this.Api.UpdateTextPr(TextPr);
	}
};
/**
 * Обновляем данные в интерфейсе о свойствах графики (картинки, автофигуры).
 * @param Flag
 * @returns {*}
 */
CDocument.prototype.Interface_Update_DrawingPr = function(Flag)
{
	var DrawingPr = this.DrawingObjects.Get_Props();

	if (true === Flag)
		return DrawingPr;
	else
	{
		if (this.Api)
		{
			for (var i = 0; i < DrawingPr.length; ++i)
				this.Api.sync_ImgPropCallback(DrawingPr[i]);
		}
	}
	if (Flag)
		return null;
};
/**
 * Обновляем данные в интерфейсе о свойствах таблицы.
 * @param Flag
 * @returns {*}
 */
CDocument.prototype.Interface_Update_TablePr = function(Flag)
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

	if (true === Flag)
		return TablePr;
	else if (null != TablePr)
		this.Api.sync_TblPropCallback(TablePr);
};
/**
 * Обновляем данные в интерфейсе о свойствах колонотитулов.
 */
CDocument.prototype.Interface_Update_HdrFtrPr = function()
{
	if (docpostype_HdrFtr === this.Get_DocPosType())
	{
		this.Api.sync_HeadersAndFootersPropCallback(this.HdrFtr.Get_Props());
	}
};
CDocument.prototype.Internal_GetContentPosByXY = function(X, Y, PageNum, ColumnsInfo)
{
    if (!ColumnsInfo)
        ColumnsInfo = {Column : 0, ColumnsCount : 1};

    if (undefined === PageNum || null === PageNum)
        PageNum = this.CurPage;

    // Сначала проверим Flow-таблицы
    var FlowTable = this.DrawingObjects.getTableByXY(X, Y, PageNum, this);
    if (null != FlowTable)
    {
        var ElementPos;
        if (flowobject_Table === FlowTable.Get_Type())
        {
            ElementPos = FlowTable.Table.Index;
        }
        else
        {
            var Frame = FlowTable;

            var StartPos  = Frame.StartIndex;
            var FlowCount = Frame.FlowCount;

            for (var Pos = StartPos; Pos < StartPos + FlowCount; ++Pos)
            {
                var Item = this.Content[Pos];

                if (Y < Item.Pages[0].Bounds.Bottom)
                    return Pos;
            }

            ElementPos = StartPos + FlowCount - 1;
        }

        var Element              = this.Content[ElementPos];
        ColumnsInfo.Column       = Element.Get_StartColumn();
        ColumnsInfo.ColumnsCount = Element.Get_ColumnsCount();
        return ElementPos;
    }

    // Теперь проверим пустые параграфы с окончанием секций
    var SectCount = this.Pages[PageNum].EndSectionParas.length;
    for (var Index = 0; Index < SectCount; ++Index)
    {
        var Item   = this.Pages[PageNum].EndSectionParas[Index];
        var Bounds = Item.Pages[0].Bounds;

        if (Y < Bounds.Bottom && Y > Bounds.Top && X > Bounds.Left && X < Bounds.Right)
        {
            var Element              = this.Content[Item.Index];
            ColumnsInfo.Column       = Element.Get_StartColumn();
            ColumnsInfo.ColumnsCount = Element.Get_ColumnsCount();
            return Item.Index;
        }
    }

    // Сначала мы определим секцию и колонку, в которую попали
    var Page = this.Pages[PageNum];

    var SectionIndex = 0;
    for (var SectionsCount = Page.Sections.length; SectionIndex < SectionsCount - 1; ++SectionIndex)
    {
        if (Y < Page.Sections[SectionIndex + 1].Y)
            break;
    }

    var PageSection  = this.Pages[PageNum].Sections[SectionIndex];
    var ColumnsCount = PageSection.Columns.length;
    var ColumnIndex  = 0;
    for (; ColumnIndex < ColumnsCount - 1; ++ColumnIndex)
    {
        if (X < (PageSection.Columns[ColumnIndex].XLimit + PageSection.Columns[ColumnIndex + 1].X) / 2)
            break;
    }

    // TODO: Разобраться с ситуацией, когда пустые колонки стоят не только в конце
    while (ColumnIndex > 0 && true === PageSection.Columns[ColumnIndex].Empty)
        ColumnIndex--;

    ColumnsInfo.Column       = ColumnIndex;
    ColumnsInfo.ColumnsCount = ColumnsCount;

    var Column   = PageSection.Columns[ColumnIndex];
    var StartPos = Column.Pos;
    var EndPos   = Column.EndPos;

    // Сохраним позиции всех Inline элементов на данной странице
    var InlineElements = [];
    for (var Index = StartPos; Index <= EndPos; Index++)
    {
        var Item = this.Content[Index];

        var PrevItem       = Item.Get_DocumentPrev();
        var bEmptySectPara = (type_Paragraph === Item.GetType() && undefined !== Item.Get_SectionPr() && true === Item.IsEmpty() && null !== PrevItem && (type_Paragraph !== PrevItem.GetType() || undefined === PrevItem.Get_SectionPr())) ? true : false;

        if (false != Item.Is_Inline() && (type_Paragraph !== Item.GetType() || false === bEmptySectPara))
            InlineElements.push(Index);
    }

    var Count = InlineElements.length;
    if (Count <= 0)
        return Math.min(Math.max(0, Page.EndPos), this.Content.length - 1);

    for (var Pos = 0; Pos < Count - 1; ++Pos)
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
CDocument.prototype.RemoveSelection = function(bNoCheckDrawing)
{
	this.Reset_WordSelection();
	this.Controller.RemoveSelection(bNoCheckDrawing);
};
CDocument.prototype.IsSelectionEmpty = function(bCheckHidden)
{
	return this.Controller.IsSelectionEmpty(bCheckHidden);
};
CDocument.prototype.DrawSelectionOnPage = function(PageAbs)
{
	this.DrawingDocument.UpdateTargetTransform(null);
	this.DrawingDocument.SetTextSelectionOutline(false);
	this.Controller.DrawSelectionOnPage(PageAbs);
};
CDocument.prototype.GetSelectionBounds = function()
{
	return this.Controller.GetSelectionBounds();
};
CDocument.prototype.Selection_SetStart         = function(X, Y, MouseEvent)
{
	this.Reset_WordSelection();

    var bInText      = (null === this.IsInText(X, Y, this.CurPage) ? false : true);
    var bTableBorder = (null === this.IsTableBorder(X, Y, this.CurPage) ? false : true);
    var nInDrawing   = this.DrawingObjects.IsInDrawingObject(X, Y, this.CurPage, this);
	var bFlowTable   = (null === this.DrawingObjects.getTableByXY(X, Y, this.CurPage, this) ? false : true);

    // Сначала посмотрим, попалили мы в текстовый селект (но при этом не в границу таблицы и не более чем одинарным кликом)
    if (-1 !== this.Selection.DragDrop.Flag && MouseEvent.ClickCount <= 1 && false === bTableBorder &&
        ( nInDrawing < 0 || ( nInDrawing === DRAWING_ARRAY_TYPE_BEHIND && true === bInText ) || ( nInDrawing > -1 && ( docpostype_DrawingObjects === this.CurPos.Type || ( docpostype_HdrFtr === this.CurPos.Type && docpostype_DrawingObjects === this.HdrFtr.CurHdrFtr.Content.CurPos.Type ) ) && true === this.DrawingObjects.isSelectedText() && null !== this.DrawingObjects.getMajorParaDrawing() && this.DrawingObjects.getGraphicInfoUnderCursor(this.CurPage, X, Y).cursorType === "text" ) ) &&
        true === this.CheckPosInSelection(X, Y, this.CurPage, undefined))
    {
        // Здесь мы сразу не начинаем перемещение текста. Его мы начинаем, курсор хотя бы немного изменит свою позицию,
        // это проверяется на MouseMove.
        // TODO: В ворде кроме изменения положения мыши, также запускается таймер для стартования drag-n-drop по времени,
        //       его можно здесь вставить.

        this.Selection.DragDrop.Flag = 1;
        this.Selection.DragDrop.Data = {X : X, Y : Y, PageNum : this.CurPage};
        return;
    }

    var bCheckHdrFtr = true;
	var bFootnotes = false;

	var nDocPosType = this.Get_DocPosType();
    if (docpostype_HdrFtr === nDocPosType)
    {
        bCheckHdrFtr         = false;
        this.Selection.Start = true;
        this.Selection.Use   = true;
        if (false != this.HdrFtr.Selection_SetStart(X, Y, this.CurPage, MouseEvent, false))
            return;

        this.Selection.Start = false;
        this.Selection.Use   = false;
        this.DrawingDocument.ClearCachePages();
        this.DrawingDocument.FirePaint();
        this.DrawingDocument.EndTrackTable(null, true);
    }
	else
	{
		bFootnotes = this.Footnotes.CheckHitInFootnote(X, Y, this.CurPage);
	}

    var PageMetrics = this.Get_PageContentStartPos(this.CurPage, this.Pages[this.CurPage].Pos);

	var oldDocPosType = this.Get_DocPosType();
    // Проверяем, не попали ли мы в колонтитул (если мы попадаем в Flow-объект, то попадание в колонтитул не проверяем)
    if (true != bFlowTable && nInDrawing < 0 && true === bCheckHdrFtr && MouseEvent.ClickCount >= 2 && ( Y <= PageMetrics.Y || Y > PageMetrics.YLimit ))
    {
        // Если был селект, тогда убираем его
        if (true === this.Selection.Use)
            this.RemoveSelection();

        this.Set_DocPosType(docpostype_HdrFtr);

        // Переходим к работе с колонтитулами
        MouseEvent.ClickCount = 1;
        this.HdrFtr.Selection_SetStart(X, Y, this.CurPage, MouseEvent, true);
        this.Interface_Update_HdrFtrPr();

        this.DrawingDocument.ClearCachePages();
        this.DrawingDocument.FirePaint();
        this.DrawingDocument.EndTrackTable(null, true);
    }
	else if (true !== bFlowTable && nInDrawing < 0 && true === bFootnotes)
	{
		this.RemoveSelection();
        this.Selection.Start = true;
        this.Selection.Use   = true;

		this.Set_DocPosType(docpostype_Footnotes);
		this.Footnotes.StartSelection(X, Y, this.CurPage, MouseEvent);
	}
    else if (nInDrawing === DRAWING_ARRAY_TYPE_BEFORE || nInDrawing === DRAWING_ARRAY_TYPE_INLINE || ( false === bTableBorder && false === bInText && nInDrawing >= 0 ))
    {
        if (docpostype_DrawingObjects != this.CurPos.Type)
            this.RemoveSelection();

        // Прячем курсор
        this.DrawingDocument.TargetEnd();
        this.DrawingDocument.SetCurrentPage(this.CurPage);

        this.Selection.Use   = true;
        this.Selection.Start = true;
        this.Selection.Flag  = selectionflag_Common;
        this.Set_DocPosType(docpostype_DrawingObjects);
        this.DrawingObjects.OnMouseDown(MouseEvent, X, Y, this.CurPage);
    }
    else
    {
        var bOldSelectionIsCommon = true;

        if (docpostype_DrawingObjects === this.CurPos.Type && true != this.IsInDrawing(X, Y, this.CurPage))
        {
            this.DrawingObjects.resetSelection();
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
		var ElementPageIndex = this.private_GetElementPageIndexByXY(ContentPos, X, Y, this.CurPage);
		var bTableBorder     = null === Item.IsTableBorder(X, Y, ElementPageIndex) ? false : true;

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
			this.Selection_SetEnd(X, Y, {Type : AscCommon.g_mouse_event_type_up, ClickCount : 1});
			this.Selection.Use    = true;
			this.Selection.Start  = true;
			this.Selection.EndPos = ContentPos;
			this.Selection.Data   = null;
		}
		else
		{
			var ElementPageIndex = this.private_GetElementPageIndexByXY(ContentPos, X, Y, this.CurPage);
			Item.Selection_SetStart(X, Y, ElementPageIndex, MouseEvent, bTableBorder);
			Item.Selection_SetEnd(X, Y, ElementPageIndex, {
				Type       : AscCommon.g_mouse_event_type_move,
				ClickCount : 1
			}, bTableBorder);

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

	//при переходе из колонтитула в контент(и обратно) необходимо скрывать иконку с/в
	var newDocPosType = this.Get_DocPosType();
    if((docpostype_HdrFtr === newDocPosType && docpostype_Content === oldDocPosType) || (docpostype_Content === newDocPosType && docpostype_HdrFtr === oldDocPosType))
    {
		window['AscCommon'].g_clipboardBase.SpecialPasteButton_Hide();
    }
};
/**
 * Данная функция может использоваться как при движении, так и при окончательном выставлении селекта.
 * Если bEnd = true, тогда это конец селекта.
 * @param X
 * @param Y
 * @param MouseEvent
 */
CDocument.prototype.Selection_SetEnd = function(X, Y, MouseEvent)
{
	this.Reset_WordSelection();

	// Работаем с колонтитулом
	if (docpostype_HdrFtr === this.CurPos.Type)
    {
        this.HdrFtr.Selection_SetEnd(X, Y, this.CurPage, MouseEvent);
        if (AscCommon.g_mouse_event_type_up == MouseEvent.Type)
        {
            if (true != this.DrawingObjects.isPolylineAddition())
                this.Selection.Start = false;
            else
                this.Selection.Start = true;
        }

        return;
    }
    else if (docpostype_DrawingObjects === this.CurPos.Type)
    {
        if (AscCommon.g_mouse_event_type_up == MouseEvent.Type)
        {
            this.DrawingObjects.OnMouseUp(MouseEvent, X, Y, this.CurPage);

            if (true != this.DrawingObjects.isPolylineAddition())
            {
                this.Selection.Start = false;
                this.Selection.Use   = true;
            }
            else
            {
                this.Selection.Start = true;
                this.Selection.Use   = true;
            }
        }
        else
        {
            this.DrawingObjects.OnMouseMove(MouseEvent, X, Y, this.CurPage);
        }
        return;
    }
	else if (docpostype_Footnotes === this.CurPos.Type)
	{
		this.Footnotes.EndSelection(X, Y, this.CurPage, MouseEvent);

		if (AscCommon.g_mouse_event_type_up == MouseEvent.Type)
			this.Selection.Start = false;

		return;
	}

    // Обрабатываем движение границы у таблиц
    if (true === this.IsMovingTableBorder())
    {
        var Item             = this.Content[this.Selection.Data.Pos];
        var ElementPageIndex = this.private_GetElementPageIndexByXY(this.Selection.Data.Pos, X, Y, this.CurPage);
        Item.Selection_SetEnd(X, Y, ElementPageIndex, MouseEvent, true);

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
                editor.sync_HyperlinkClickCallback(this.Selection.Data.Hyperlink.Get_Value());
                this.Selection.Data.Hyperlink.Set_Visited(true);

                for (var PageIdx = Item.Get_StartPage_Absolute(); PageIdx < Item.Get_StartPage_Absolute() + Item.Pages.length; PageIdx++)
                    this.DrawingDocument.OnRecalculatePage(PageIdx, this.Pages[PageIdx]);

                this.DrawingDocument.OnEndRecalculate(false, true);
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

    // TODO: Разрулить пустой селект
    // Чтобы не было эффекта, когда ничего не поселекчено, а при удалении соединяются параграфы

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

    var ElementPageIndex = this.private_GetElementPageIndexByXY(ContentPos, X, Y, this.CurPage);
    this.Content[ContentPos].Selection_SetEnd(X, Y, ElementPageIndex, MouseEvent);

    // Проверяем, чтобы у нас в селект не попали элементы, в которых не выделено ничего
    if (true === this.Content[End].IsSelectionEmpty() && true === this.CheckEmptyElementsOnSelection)
    {
        this.Content[End].RemoveSelection();
        End--;
    }

    if (Start != End && true === this.Content[Start].IsSelectionEmpty() && true === this.CheckEmptyElementsOnSelection)
    {
        this.Content[Start].RemoveSelection();
        Start++;
    }

    if (Direction > 0)
    {
        this.Selection.StartPos = Start;
        this.Selection.EndPos   = End;
    }
    else
    {
        this.Selection.StartPos = End;
        this.Selection.EndPos   = Start;
    }
};
/**
 * Получаем направление селекта
 * @returns {number} Возвращается направление селекта. 1 - нормальное направление, -1 - обратное
 */
CDocument.prototype.GetSelectDirection = function()
{
	var oStartPos = this.GetContentPosition(true, true);
	var oEndPos   = this.GetContentPosition(true, false);

	for (var nPos = 0, nLen = Math.min(oStartPos.length, oEndPos.length); nPos < nLen; ++nPos)
	{
		if (!oEndPos[nPos] || !oStartPos[nPos] || oStartPos[nPos].Class !== oEndPos[nPos].Class)
			return 1;

		if (oStartPos[nPos].Position < oEndPos[nPos].Position)
			return 1;
		else if (oStartPos[nPos].Position > oEndPos[nPos].Position)
			return -1;
	}

	return 1;
};
CDocument.prototype.IsMovingTableBorder = function()
{
	return this.Controller.IsMovingTableBorder();
};
/**
 * Проверяем попали ли мы в селект.
 * @param X
 * @param Y
 * @param PageAbs
 * @param NearPos
 * @returns {boolean}
 */
CDocument.prototype.CheckPosInSelection = function(X, Y, PageAbs, NearPos)
{
	return this.Controller.CheckPosInSelection(X, Y, PageAbs, NearPos);
};
/**
 * Выделяем все содержимое, в зависимости от текущего положения курсора.
 */
CDocument.prototype.SelectAll = function()
{
	this.private_UpdateTargetForCollaboration();

	this.Reset_WordSelection();
	this.Controller.SelectAll();

	// TODO: Пока делаем Start = true, чтобы при Ctrl+A не происходил переход к концу селекта, надо будет
	//       сделать по нормальному
	this.Selection.Start = true;
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
	this.Document_UpdateRulersState();
	this.Selection.Start = false;

	// Отдельно обрабатываем это событие, потому что внутри него идет проверка на this.Selection.Start !== true
	this.Document_UpdateCopyCutState();

	this.private_UpdateCursorXY(true, true);
};
CDocument.prototype.On_DragTextEnd = function(NearPos, bCopy)
{
    if (true === this.Comments.Is_Use())
    {
        this.SelectComment(null, false);
        editor.sync_HideComment();
    }

    // Сначала нам надо проверить попадаем ли мы обратно в выделенный текст, если да, тогда ничего не делаем,
    // а если нет, тогда удаляем выделенный текст и вставляем его в заданное место.

    if (true === this.CheckPosInSelection(0, 0, 0, NearPos))
    {
        this.RemoveSelection();

        // Нам надо снять селект и поставить курсор в то место, где была ближайшая позиция
        var Paragraph = NearPos.Paragraph;
        Paragraph.Cursor_MoveToNearPos(NearPos);
        Paragraph.Document_SetThisElementCurrent(false);

        this.Document_UpdateSelectionState();
        this.Document_UpdateInterfaceState();
        this.Document_UpdateRulersState();
    }
    else
    {
        // Создаем сразу точку в истории, т.к. при выполнении функции GetSelectedContent нам надо, чтобы данная
        // точка уже набивалась изменениями. Если из-за совместного редактирования действие сделать невозможно будет,
        // тогда последнюю точку удаляем.
        History.Create_NewPoint(AscDFH.historydescription_Document_DragText);

        NearPos.Paragraph.Check_NearestPos(NearPos);

        // Получим копию выделенной части документа, которую надо перенести в новое место, одновременно с этим
        // удаляем эту выделенную часть (если надо).

        var DocContent = this.GetSelectedContent(true);

        if (false === this.Can_InsertContent(DocContent, NearPos))
        {
            this.History.Remove_LastPoint();
			NearPos.Paragraph.Clear_NearestPosArray();
            return;
        }

        var Para = NearPos.Paragraph;

        // Если мы копируем, тогда не надо проверять выделенные параграфы, а если переносим, тогда проверяем
        var CheckChangesType = (true !== bCopy ? AscCommon.changestype_Document_Content : changestype_None);
        if (false === this.Document_Is_SelectionLocked(CheckChangesType, {
                Type      : changestype_2_ElementsArray_and_Type,
                Elements  : [Para],
                CheckType : changestype_Paragraph_Content
            }, true))
        {
            // Если надо удаляем выделенную часть (пересчет отключаем на время удаления)
            if (true !== bCopy)
            {
                this.TurnOff_Recalculate();
                this.TurnOff_InterfaceEvents();
                this.Remove(1, false, false, false);
                this.TurnOn_Recalculate(false);
                this.TurnOn_InterfaceEvents(false);

                if (false === Para.Is_UseInDocument())
                {
                    this.Document_Undo();
                    this.History.Clear_Redo();
                    return;
                }
            }

            this.RemoveSelection(true);

            // Выделение выставляется внутри функции Insert_Content
            Para.Parent.Insert_Content(DocContent, NearPos);

            this.Recalculate();

            this.Document_UpdateSelectionState();
            this.Document_UpdateInterfaceState();
            this.Document_UpdateRulersState();
        }
        else
		{
			this.History.Remove_LastPoint();
			NearPos.Paragraph.Clear_NearestPosArray();
		}
    }
};
/**
 * В данной функции мы получаем выделенную часть документа в формате класса CSelectedContent.
 * @param bUseHistory - нужна ли запись в историю созданных классов. (при drag-n-drop нужна, при копировании не нужна)
 * @returns {CSelectedContent}
 */
CDocument.prototype.GetSelectedContent = function(bUseHistory)
{
	// При копировании нам не нужно, чтобы новые классы помечались как созданные в рецензировании, а при перетаскивании
	// нужно.
	var isTrack = this.Is_TrackRevisions() && !bUseHistory;
	if (isTrack)
		this.Set_TrackRevisions(false);

	var bNeedTurnOffTableId = g_oTableId.m_bTurnOff === false && true !== bUseHistory;
	if (!bUseHistory)
		History.TurnOff();

	if (bNeedTurnOffTableId)
	{
		g_oTableId.m_bTurnOff = true;
	}

	var SelectedContent = new CSelectedContent();
	this.Controller.GetSelectedContent(SelectedContent);
	SelectedContent.On_EndCollectElements(this, false);

	if (!bUseHistory)
		History.TurnOn();

	if (bNeedTurnOffTableId)
	{
		g_oTableId.m_bTurnOff = false;
	}

	if (isTrack)
		this.Set_TrackRevisions(true);

	return SelectedContent;
};
CDocument.prototype.Can_InsertContent = function(SelectedContent, NearPos)
{
	// Проверяем, что вставка не пустая
	if (SelectedContent.Elements.length <= 0)
		return false;

	var Para = NearPos.Paragraph;

	// Автофигуры не вставляем в другие автофигуры
	if (true === Para.Parent.Is_DrawingShape() && true === SelectedContent.HaveShape)
		return false;


	//В заголовки диаграмм не вставляем формулы и любые DrawingObjects
	if (Para.bFromDocument === false && (SelectedContent.DrawingObjects.length > 0 || SelectedContent.HaveMath))
		return false;

	// Проверяем корректность места, куда вставляем
	var ParaNearPos = NearPos.Paragraph.Get_ParaNearestPos(NearPos);
	if (null === ParaNearPos || ParaNearPos.Classes.length < 2)
		return false;

	var LastClass = ParaNearPos.Classes[ParaNearPos.Classes.length - 1];
	if (para_Math_Run === LastClass.Type)
	{
		// Проверяем, что вставляемый контент тоже формула
		var Element = SelectedContent.Elements[0].Element;
		if (1 !== SelectedContent.Elements.length || type_Paragraph !== Element.GetType() || null === LastClass.Parent)
			return false;

        if(!SelectedContent.CanConvertToMath)
        {
            var Math = null;
            var Count = Element.Content.length;
            for (var Index = 0; Index < Count; Index++) {
                var Item = Element.Content[Index];
                if (para_Math === Item.Type && null === Math)
                    Math = Element.Content[Index];
                else if (true !== Item.Is_Empty({SkipEnd: true}))
                    return false;
            }
        }
	}
	else if (para_Run !== LastClass.Type)
		return false;

	if (null === Para.Parent || undefined === Para.Parent)
		return false;

	return true;
};
CDocument.prototype.Insert_Content = function(SelectedContent, NearPos)
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

        if(null === InsertMathContent)
        {
            //try to convert content to ParaMath in simple cases.
            InsertMathContent = SelectedContent.ConvertToMath();
        }

        if (null !== InsertMathContent)
		{
			MathContent.Add_ToContent(MathContentPos + 1, NewMathRun);
			MathContent.Insert_MathContent(InsertMathContent.Root, MathContentPos + 1, true);
		}
	}
	else if (para_Run === LastClass.Type)
	{
		var NearContentPos = NearPos.ContentPos;
		// Сначала найдем номер элемента, начиная с которого мы будем производить вставку
		var DstIndex       = -1;
		var Count          = this.Content.length;
		for (var Index = 0; Index < Count; Index++)
		{
			if (this.Content[Index] === Para)
			{
				DstIndex = Index;
				break;
			}
		}

		if (-1 === DstIndex)
			return false;

		var Elements      = SelectedContent.Elements;
		var ElementsCount = Elements.length;
		var FirstElement  = SelectedContent.Elements[0];
		if (1 === ElementsCount && true !== FirstElement.SelectedAll && type_Paragraph === FirstElement.Element.GetType() && true !== FirstElement.Element.Is_Empty())
		{
			// Нам нужно в заданный параграф вставить выделенный текст
			var NewPara          = FirstElement.Element;
			var NewElementsCount = NewPara.Content.length - 1; // Последний ран с para_End не добавляем

			var LastClass  = ParaNearPos.Classes[ParaNearPos.Classes.length - 1];
			var NewElement = LastClass.Split(ParaNearPos.NearPos.ContentPos, ParaNearPos.Classes.length - 1);
			var PrevClass  = ParaNearPos.Classes[ParaNearPos.Classes.length - 2];
			var PrevPos    = ParaNearPos.NearPos.ContentPos.Data[ParaNearPos.Classes.length - 2];

			PrevClass.Add_ToContent(PrevPos + 1, NewElement);

			// TODO: Заглушка для переноса автофигур и картинок. Когда разрулим ситуацию так, чтобы когда у нас
			//       в текста была выделена автофигура выделение шло для автофигур, тогда здесь можно будет убрать.
			var bNeedSelect = (true === SelectedContent.MoveDrawing ? false : true);

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

			var bAddEmptyPara          = false;
			var bDoNotIncreaseDstIndex = false;

			if (true === Para.IsCursorAtEnd())
			{
				bConcatE = false;

				if (1 === ElementsCount && type_Paragraph === FirstElement.Element.GetType() && ( true === FirstElement.Element.Is_Empty() || true == FirstElement.SelectedAll ))
				{
					bConcatS = false;

					// TODO: Возможно флаг bDoNotIncreaseDstIndex не нужен, и здесь не нужно увеличивать индекс DstIndex
					if (type_Paragraph !== this.Content[DstIndex].Get_Type() || true !== this.Content[DstIndex].Is_Empty())
					{
						DstIndex++;
						bDoNotIncreaseDstIndex = true;
					}
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
				var NewParagraph = new Paragraph(this.DrawingDocument, this);
				Para.Split(NewParagraph);
				this.Internal_Content_Add(DstIndex + 1, NewParagraph);

				ParaE      = NewParagraph;
				ParaEIndex = DstIndex + 1;
			}

			var NewEmptyPara = null;
			if (true === bAddEmptyPara)
			{
				// Создаем новый параграф
				NewEmptyPara = new Paragraph(this.DrawingDocument, this);
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
			else if (true !== Para.IsCursorAtBegin() && true !== bDoNotIncreaseDstIndex)
			{
				DstIndex++;
			}

			var EndIndex = ElementsCount - 1;
			if (true === bConcatE && StartIndex < EndIndex)
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

			this.Selection.Use      = true;
			this.Selection.StartPos = DstIndex;
			this.Selection.EndPos   = LastPos;
			this.CurPos.ContentPos  = LastPos;
		}

		if (docpostype_DrawingObjects !== this.CurPos.Type)
			this.Set_DocPosType(docpostype_Content);
	}
};
CDocument.prototype.Document_SelectNumbering = function(NumPr, Index)
{
	this.private_UpdateTargetForCollaboration();

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

	this.Interface_Update_ParaPr();
	this.Interface_Update_TextPr();

	this.Document_UpdateSelectionState();
};
CDocument.prototype.Remove_NumberingSelection = function()
{
	if (true === this.Selection.Use && selectionflag_Numbering == this.Selection.Flag)
		this.RemoveSelection();
};
CDocument.prototype.UpdateCursorType = function(X, Y, PageAbs, MouseEvent)
{
	if (null !== this.FullRecalc.Id && this.FullRecalc.PageIndex <= PageAbs)
		return;

	this.Api.sync_MouseMoveStartCallback();

	this.DrawingDocument.OnDrawContentControl(null, c_oContentControlTrack.Hover);

	if (true === this.DrawingDocument.IsCursorInTableCur(X, Y, PageAbs))
	{
		this.DrawingDocument.SetCursorType("default", new AscCommon.CMouseMoveData());
		this.Api.sync_MouseMoveEndCallback();
		return;
	}

	var nDocPosType = this.Get_DocPosType();
	if (docpostype_HdrFtr === nDocPosType)
	{
		this.HeaderFooterController.UpdateCursorType(X, Y, PageAbs, MouseEvent);
	}
	else if (docpostype_DrawingObjects === nDocPosType)
	{
		this.DrawingsController.UpdateCursorType(X, Y, PageAbs, MouseEvent);
	}
	else
	{
		if (true === this.Footnotes.CheckHitInFootnote(X, Y, PageAbs))
			this.Footnotes.UpdateCursorType(X, Y, PageAbs, MouseEvent);
		else
			this.LogicDocumentController.UpdateCursorType(X, Y, PageAbs, MouseEvent);
	}

	this.Api.sync_MouseMoveEndCallback();
};
/**
 * Проверяем попадание в границу таблицы.
 * @param X
 * @param Y
 * @param PageIndex
 * @returns {?CTable} null - не попали, а если попали возвращается указатель на таблицу
 */
CDocument.prototype.IsTableBorder = function(X, Y, PageIndex)
{
	if (PageIndex >= this.Pages.length || PageIndex < 0)
		return null;

	if (docpostype_HdrFtr === this.Get_DocPosType())
	{
		return this.HdrFtr.IsTableBorder(X, Y, PageIndex);
	}
	else
	{
		if (-1 != this.DrawingObjects.IsInDrawingObject(X, Y, PageIndex, this))
		{
			return null;
		}
		else if (true === this.Footnotes.CheckHitInFootnote(X, Y, PageIndex))
		{
			return this.Footnotes.IsTableBorder(X, Y, PageIndex);
		}
		else
		{
			var ColumnsInfo      = {};
			var ElementPos       = this.Internal_GetContentPosByXY(X, Y, PageIndex, ColumnsInfo);
			var Element          = this.Content[ElementPos];
			var ElementPageIndex = this.private_GetElementPageIndex(ElementPos, PageIndex, ColumnsInfo.Column, ColumnsInfo.Column, ColumnsInfo.ColumnsCount);
			return Element.IsTableBorder(X, Y, ElementPageIndex);
		}
	}
};
/**
 * Проверяем, попали ли мы четко в текст (не лежащий в автофигуре)
 * @param X
 * @param Y
 * @param PageIndex
 * @returns {*}
 */
CDocument.prototype.IsInText = function(X, Y, PageIndex)
{
	if (PageIndex >= this.Pages.length || PageIndex < 0)
		return null;

	if (docpostype_HdrFtr === this.Get_DocPosType())
	{
		return this.HdrFtr.IsInText(X, Y, PageIndex);
	}
	else
	{
		if (true === this.Footnotes.CheckHitInFootnote(X, Y, PageIndex))
		{
			return this.Footnotes.IsInText(X, Y, PageIndex);
		}
		else
		{
			var ContentPos       = this.Internal_GetContentPosByXY(X, Y, PageIndex);
			var ElementPageIndex = this.private_GetElementPageIndexByXY(ContentPos, X, Y, PageIndex);
			var Item             = this.Content[ContentPos];
			return Item.IsInText(X, Y, ElementPageIndex);
		}
	}
};
CDocument.prototype.Get_ParentTextTransform = function()
{
	return null;
};
/**
 * Проверяем, попали ли мы в автофигуру данного DocumentContent
 * @param X
 * @param Y
 * @param PageIndex
 * @returns {*}
 */
CDocument.prototype.IsInDrawing = function(X, Y, PageIndex)
{
	if (docpostype_HdrFtr === this.Get_DocPosType())
	{
		return this.HdrFtr.IsInDrawing(X, Y, PageIndex);
	}
	else
	{
		if (-1 != this.DrawingObjects.IsInDrawingObject(X, Y, this.CurPage, this))
		{
			return true;
		}
		else if (true === this.Footnotes.CheckHitInFootnote(X, Y, PageIndex))
		{
			return this.Footnotes.IsInDrawing(X, Y, PageIndex);
		}
		else
		{
			var ContentPos       = this.Internal_GetContentPosByXY(X, Y, PageIndex);
			var Item             = this.Content[ContentPos];
			var ElementPageIndex = this.private_GetElementPageIndexByXY(ContentPos, X, Y, PageIndex);
			return Item.IsInDrawing(X, Y, ElementPageIndex);
		}
	}
};
CDocument.prototype.Is_UseInDocument = function(Id)
{
	var Count = this.Content.length;
	for (var Index = 0; Index < Count; Index++)
	{
		if (Id === this.Content[Index].GetId())
			return true;
	}

	return false;
};
CDocument.prototype.OnKeyDown = function(e)
{
    var OldRecalcId = this.RecalcId;

    // Если мы только что расширяли документ двойным щелчком, то сохраняем это действие
    if (true === this.History.Is_ExtendDocumentToPos())
        this.History.Clear_Additional();

    // Сбрасываем текущий элемент в поиске
    if (this.SearchEngine.Count > 0)
        this.SearchEngine.Reset_Current();

    var bUpdateSelection = true;
    var bRetValue        = keydownresult_PreventNothing;

    if (e.KeyCode == 8) // BackSpace
    {
        if (false === this.Document_Is_SelectionLocked(AscCommon.changestype_Remove, null, true, this.IsFormFieldEditing()))
        {
            this.Create_NewHistoryPoint(AscDFH.historydescription_Document_BackSpaceButton);
            this.Remove(-1, true);
        }
        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 9) // Tab
    {
        var SelectedInfo = this.GetSelectedElementsInfo();

        if (null !== SelectedInfo.Get_Math())
        {
            var ParaMath  = SelectedInfo.Get_Math();
            var Paragraph = ParaMath.GetParagraph();
            if (Paragraph && false === this.Document_Is_SelectionLocked(changestype_None, {
                    Type      : changestype_2_Element_and_Type,
                    Element   : Paragraph,
                    CheckType : changestype_Paragraph_Content
                }))
            {
                this.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddTabToMath);
                ParaMath.Handle_Tab(!e.ShiftKey);
                this.Recalculate();
            }
        }
        else if (true === SelectedInfo.Is_InTable() && true != e.CtrlKey)
        {
            this.MoveCursorToCell(true === e.ShiftKey ? false : true);
        }
        else if (true === SelectedInfo.Is_DrawingObjSelected() && true != e.CtrlKey)
        {
            this.DrawingObjects.selectNextObject(( e.ShiftKey === true ? -1 : 1 ));
        }
        else
        {
            if (true === SelectedInfo.Is_MixedSelection())
            {
                if (true === e.ShiftKey)
                    this.DecreaseIndent();
                else
                    this.IncreaseIndent();
            }
            else
            {
                var Paragraph = SelectedInfo.GetParagraph();
                var ParaPr    = Paragraph.Get_CompiledPr2(false).ParaPr;
                if (null != Paragraph && ( true === Paragraph.IsCursorAtBegin() || true === Paragraph.Selection_IsFromStart() ) && ( undefined != Paragraph.Numbering_Get() || ( true != Paragraph.IsEmpty() && ParaPr.Tabs.Tabs.length <= 0 ) ))
                {
                    if (false === this.Document_Is_SelectionLocked(changestype_None, {
                            Type      : changestype_2_Element_and_Type,
                            Element   : Paragraph,
                            CheckType : AscCommon.changestype_Paragraph_Properties
                        }))
                    {
                        this.Create_NewHistoryPoint(AscDFH.historydescription_Document_MoveParagraphByTab);
                        Paragraph.Add_Tab(e.ShiftKey);
                        this.Recalculate();

                        this.Document_UpdateInterfaceState();
                        this.Document_UpdateSelectionState();
                    }
                }
                else if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
                {
                    this.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddTab);
                    this.AddToParagraph(new ParaTab());
                }
            }
        }
        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 13) // Enter
    {
        var Hyperlink = this.IsCursorInHyperlink(false);
        if (null != Hyperlink && false === e.ShiftKey)
        {
            editor.sync_HyperlinkClickCallback(Hyperlink.Get_Value());
            Hyperlink.Set_Visited(true);

            // TODO: Пока сделаем так, потом надо будет переделать
            this.DrawingDocument.ClearCachePages();
            this.DrawingDocument.FirePaint();
        }
        else
		{
			var oSelectedInfo = this.GetSelectedElementsInfo();
			var CheckType = ( e.ShiftKey || e.CtrlKey ? changestype_Paragraph_Content : AscCommon.changestype_Document_Content_Add );

			var bCanPerform = true;
			if ((oSelectedInfo.GetInlineLevelSdt() && (!e.ShiftKey || e.CtrlKey)) || (oSelectedInfo.Get_Field() && oSelectedInfo.Get_Field().IsFillingForm()))
				bCanPerform = false;

			if (bCanPerform && false === this.Document_Is_SelectionLocked(CheckType, null, false, true !== e.CtrlKey && this.IsFormFieldEditing()))
			{
				this.Create_NewHistoryPoint(AscDFH.historydescription_Document_EnterButton);

				var oMath = oSelectedInfo.Get_Math();
				if (null !== oMath && oMath.Is_InInnerContent())
				{
					if (oMath.Handle_AddNewLine())
						this.Recalculate();
				}
				else
				{
					if (e.ShiftKey && e.CtrlKey)
					{
						this.AddToParagraph(new ParaNewLine(break_Column));
					}
					else if (e.ShiftKey)
					{
						this.AddToParagraph(new ParaNewLine(break_Line));
					}
					else if (e.CtrlKey)
					{
						this.AddToParagraph(new ParaNewLine(break_Page));
					}
					else
					{
						this.AddNewParagraph();
					}
				}
			}
		}

        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 27) // Esc
    {
        // 1. Если начался drag-n-drop сбрасываем его.
        // 2. Если у нас сейчас происходит выделение маркером, тогда его отменяем
        // 3. Если у нас сейчас происходит форматирование по образцу, тогда его отменяем
        // 4. Если у нас выделена автофигура (в колонтитуле или документе), тогда снимаем выделение с нее
        // 5. Если мы просто находимся в колонтитуле (автофигура не выделена) выходим из колонтитула
        if (true === this.DrawingDocument.IsTrackText())
        {
            // Сбрасываем проверку Drag-n-Drop
            this.Selection.DragDrop.Flag = 0;
            this.Selection.DragDrop.Data = null;

            this.DrawingDocument.CancelTrackText();
        }
        else if (true === editor.isMarkerFormat)
        {
            editor.sync_MarkerFormatCallback(false);
            this.UpdateCursorType(this.CurPos.RealX, this.CurPos.RealY, this.CurPage, new AscCommon.CMouseEventHandler());
        }
        else if (c_oAscFormatPainterState.kOff !== editor.isPaintFormat)
        {
            editor.sync_PaintFormatCallback(c_oAscFormatPainterState.kOff);
            this.UpdateCursorType(this.CurPos.RealX, this.CurPos.RealY, this.CurPage, new AscCommon.CMouseEventHandler());
        }
        else if (editor.isStartAddShape)
        {
            editor.sync_StartAddShapeCallback(false);
            editor.sync_EndAddShape();
            this.UpdateCursorType(this.CurPos.RealX, this.CurPos.RealY, this.CurPage, new AscCommon.CMouseEventHandler());
        }
        else if (docpostype_DrawingObjects === this.CurPos.Type || (docpostype_HdrFtr === this.CurPos.Type && null != this.HdrFtr.CurHdrFtr && docpostype_DrawingObjects === this.HdrFtr.CurHdrFtr.Content.CurPos.Type ))
        {
        	this.EndDrawingEditing();
        }
        else if (docpostype_HdrFtr == this.CurPos.Type)
        {
            this.EndHdrFtrEditing(true);
        }

		if(window['AscCommon'].g_clipboardBase.showSpecialPasteButton)
		{
			window['AscCommon'].g_clipboardBase.SpecialPasteButton_Hide();
		}

        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 32) // Space
    {
    	var bFillingForm = false;
    	if (this.IsFormFieldEditing() && ((true === e.ShiftKey && true === e.CtrlKey) || true !== e.CtrlKey))
			bFillingForm = true;

        if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content, null, true, bFillingForm))
        {
            this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SpaceButton);

            // Если мы находимся в формуле, тогда пытаемся выполнить автозамену

            var oSelectedInfo = this.GetSelectedElementsInfo();
            var oMath         = oSelectedInfo.Get_Math();

            if (null !== oMath && true === oMath.Make_AutoCorrect())
            {
                // Ничего тут не делаем. Все делается в автозамене
            }
            else
            {
                if (true === e.ShiftKey && true === e.CtrlKey)
                {
                    this.DrawingDocument.TargetStart();
                    this.DrawingDocument.TargetShow();

                    this.AddToParagraph(new ParaText(String.fromCharCode(0x00A0)));
                }
                else if (true === e.CtrlKey)
                {
                    this.ClearParagraphFormatting();
                }
                else
                {
                    this.DrawingDocument.TargetStart();
                    this.DrawingDocument.TargetShow();

                    this.CheckLanguageOnTextAdd = true;
                    this.AddToParagraph(new ParaSpace());
                    this.CheckLanguageOnTextAdd = false;
                }
            }
        }

        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 33) // PgUp
    {
        // TODO: Реализовать Ctrl + Shift + PgUp / Ctrl + PgUp / Shift + PgUp

        if (true === e.AltKey)
        {
            var MouseEvent = new AscCommon.CMouseEventHandler();

            MouseEvent.ClickCount = 1;
            MouseEvent.Type       = AscCommon.g_mouse_event_type_down;

            this.CurPage--;

            if (this.CurPage < 0)
                this.CurPage = 0;

            this.Selection_SetStart(0, 0, MouseEvent);

            MouseEvent.Type = AscCommon.g_mouse_event_type_up;
            this.Selection_SetEnd(0, 0, MouseEvent);
        }
        else
        {
            if (docpostype_HdrFtr === this.CurPos.Type)
            {
                if (true === this.HdrFtr.GoTo_PrevHdrFtr())
                {
                    this.Document_UpdateSelectionState();
                    this.Document_UpdateInterfaceState();
                }
            }
            else
            {

                var TempXY = this.GetCursorPosXY();

                var X = TempXY.X;
                var Y = TempXY.Y;

                var Dy = this.DrawingDocument.GetVisibleMMHeight();
                if (Y - Dy < 0)
                {
                    this.CurPage--;
                    var PageH = this.Get_PageLimits(this.CurPage).YLimit;

                    Dy -= Y;
                    Y = PageH;
                    while (Dy > PageH)
                    {
                        Dy -= PageH;
                        this.CurPage--;
                    }

                    if (this.CurPage < 0)
                    {
                        this.CurPage = 0;
                        var oElement = this.Content[0];
                        Dy           = PageH - oElement.GetPageBounds(oElement.GetPagesCount() - 1).Top;
                    }
                }

                // TODO: переделать данную проверку
                if (this.CurPage >= this.DrawingDocument.m_lPagesCount)
                    this.CurPage = this.DrawingDocument.m_lPagesCount;

                var StartX = X;
                var StartY = Y;
                var CurY   = Y;

                while (Math.abs(StartY - Y) < 0.001)
                {
                    var bBreak = false;
                    CurY -= Dy;

                    if (CurY < 0)
                    {
                        this.CurPage--;
                        var PageH = this.Get_PageLimits(this.CurPage).YLimit;
                        CurY      = PageH;

                        // Эта проверка нужна для выполнения PgUp в начале документа
                        if (this.CurPage < 0)
                        {
                            this.CurPage = this.DrawingDocument.m_lPagesCount - 1;
                            CurY         = 0;
                        }

                        // Поскольку мы перешли на другую страницу, то можно из цикла выходить
                        bBreak = true;
                    }

                    this.MoveCursorToXY(StartX, CurY, false);
                    this.CurPos.RealX = StartX;
                    this.CurPos.RealY = CurY;

                    TempXY = this.GetCursorPosXY();
                    X      = TempXY.X;
                    Y      = TempXY.Y;

                    if (true === bBreak)
                        break;
                }
            }
        }

		this.private_CheckCursorPosInFillingFormMode();
        this.CheckComplexFieldsInSelection();
        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 34) // PgDn
    {
        // TODO: Реализовать Ctrl + Shift + PgDn / Ctrl + PgDn / Shift + PgDn

        if (true === e.AltKey)
        {
            var MouseEvent = new AscCommon.CMouseEventHandler();

            MouseEvent.ClickCount = 1;
            MouseEvent.Type       = AscCommon.g_mouse_event_type_down;

            this.CurPage++;

            // TODO: переделать данную проверку
            if (this.CurPage >= this.DrawingDocument.m_lPagesCount)
                this.CurPage = this.DrawingDocument.m_lPagesCount - 1;

            this.Selection_SetStart(0, 0, MouseEvent);

            MouseEvent.Type = AscCommon.g_mouse_event_type_up;
            this.Selection_SetEnd(0, 0, MouseEvent);
        }
        else
        {
            if (docpostype_HdrFtr === this.CurPos.Type)
            {
                if (true === this.HdrFtr.GoTo_NextHdrFtr())
                {
                    this.Document_UpdateSelectionState();
                    this.Document_UpdateInterfaceState();
                }
            }
            else
            {
                if (this.Pages.length > 0)
                {
                    var TempXY = this.GetCursorPosXY();

                    var X = TempXY.X;
                    var Y = TempXY.Y;

                    var Dy = this.DrawingDocument.GetVisibleMMHeight();
                    if (Y + Dy > this.Get_PageLimits(this.CurPage).YLimit)
                    {
                        this.CurPage++;
                        var PageH = this.Get_PageLimits(this.CurPage).YLimit;
                        Dy -= PageH - Y;
                        Y         = 0;
                        while (Dy > PageH)
                        {
                            Dy -= PageH;
                            this.CurPage++;
                        }

                        if (this.CurPage >= this.Pages.length)
                        {
                            this.CurPage    = this.Pages.length - 1;
                            var LastElement = this.Content[this.Pages[this.CurPage].EndPos];
                            Dy              = LastElement.GetPageBounds(LastElement.GetPagesCount() - 1).Bottom;
                        }
                    }

                    if (this.CurPage >= this.Pages.length)
                        this.CurPage = this.Pages.length - 1;

                    var StartX = X;
                    var StartY = Y;
                    var CurY   = Y;

                    while (Math.abs(StartY - Y) < 0.001)
                    {
                        var bBreak = false;
                        CurY += Dy;

                        var PageH = this.Get_PageLimits(this.CurPage).YLimit;
                        if (CurY > PageH)
                        {
                            this.CurPage++;
                            CurY = 0;

                            // Эта проверка нужна для выполнения PgDn в конце документа
                            if (this.CurPage >= this.Pages.length)
                            {
                                this.CurPage    = this.Pages.length - 1;
                                var LastElement = this.Content[this.Pages[this.CurPage].EndPos];
                                CurY            = LastElement.GetPageBounds(LastElement.GetPagesCount() - 1).Bottom;
                            }

                            // Поскольку мы перешли на другую страницу, то можно из цикла выходить
                            bBreak = true;
                        }

                        this.MoveCursorToXY(StartX, CurY, false);
                        this.CurPos.RealX = StartX;
                        this.CurPos.RealY = CurY;

                        TempXY = this.GetCursorPosXY();
                        X      = TempXY.X;
                        Y      = TempXY.Y;

                        if (true === bBreak)
                            break;
                    }
                }
            }
        }

		this.private_CheckCursorPosInFillingFormMode();
		this.CheckComplexFieldsInSelection();
        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 35) // клавиша End
    {
        if (true === e.CtrlKey) // Ctrl + End - переход в конец документа
        {
            this.MoveCursorToEndPos(true === e.ShiftKey);
        }
        else // Переходим в конец строки
        {
            this.MoveCursorToEndOfLine(true === e.ShiftKey);
        }

        this.Document_UpdateInterfaceState();
        this.Document_UpdateRulersState();

		this.private_CheckCursorPosInFillingFormMode();
		this.CheckComplexFieldsInSelection();
        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 36) // клавиша Home
    {
        if (true === e.CtrlKey) // Ctrl + Home - переход в начало документа
        {
            this.MoveCursorToStartPos(true === e.ShiftKey);
        }
        else // Переходим в начало строки
        {
            this.MoveCursorToStartOfLine(true === e.ShiftKey);
        }

        this.Document_UpdateInterfaceState();
        this.Document_UpdateRulersState();

		this.private_CheckCursorPosInFillingFormMode();
		this.CheckComplexFieldsInSelection();
        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 37) // Left Arrow
    {
        // Чтобы при зажатой клавише курсор не пропадал
        if (true != e.ShiftKey)
            this.DrawingDocument.TargetStart();

        this.DrawingDocument.UpdateTargetFromPaint = true;
        this.MoveCursorLeft(true === e.ShiftKey, true === e.CtrlKey);
		this.private_CheckCursorPosInFillingFormMode();
		this.CheckComplexFieldsInSelection();
        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 38) // Top Arrow
    {
        // TODO: Реализовать Ctrl + Up/ Ctrl + Shift + Up
        // Чтобы при зажатой клавише курсор не пропадал
        if (true != e.ShiftKey)
            this.DrawingDocument.TargetStart();

        this.DrawingDocument.UpdateTargetFromPaint = true;
        this.MoveCursorUp(true === e.ShiftKey, true === e.CtrlKey);
		this.private_CheckCursorPosInFillingFormMode();
		this.CheckComplexFieldsInSelection();
        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 39) // Right Arrow
    {
        // Чтобы при зажатой клавише курсор не пропадал
        if (true != e.ShiftKey)
            this.DrawingDocument.TargetStart();

        this.DrawingDocument.UpdateTargetFromPaint = true;
        this.MoveCursorRight(true === e.ShiftKey, true === e.CtrlKey);
		this.private_CheckCursorPosInFillingFormMode();
		this.CheckComplexFieldsInSelection();
        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 40) // Bottom Arrow
    {
        // TODO: Реализовать Ctrl + Down/ Ctrl + Shift + Down
        // Чтобы при зажатой клавише курсор не пропадал
        if (true != e.ShiftKey)
            this.DrawingDocument.TargetStart();

        this.DrawingDocument.UpdateTargetFromPaint = true;
        this.MoveCursorDown(true === e.ShiftKey, true === e.CtrlKey);
		this.private_CheckCursorPosInFillingFormMode();
		this.CheckComplexFieldsInSelection();
        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 46) // Delete
    {
        if (true != e.ShiftKey)
        {
            if (false === this.Document_Is_SelectionLocked(AscCommon.changestype_Delete, null, true, this.IsFormFieldEditing()))
            {
                this.Create_NewHistoryPoint(AscDFH.historydescription_Document_DeleteButton);
                this.Remove(1, true);
            }
            bRetValue = keydownresult_PreventAll;
        }
    }
    else if (e.KeyCode == 49 && true === e.AltKey && !e.AltGr) // Alt + Ctrl + Num1 - применяем стиль Heading1
    {
        if (false === this.Document_Is_SelectionLocked(AscCommon.changestype_Paragraph_Properties))
        {
            this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetStyleHeading1);
            this.SetParagraphStyle("Heading 1");
            this.Document_UpdateInterfaceState();
        }
        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 50 && true === e.AltKey && !e.AltGr) // Alt + Ctrl + Num2 - применяем стиль Heading2
    {
        if (false === this.Document_Is_SelectionLocked(AscCommon.changestype_Paragraph_Properties))
        {
            this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetStyleHeading2);
            this.SetParagraphStyle("Heading 2");
            this.Document_UpdateInterfaceState();
        }
        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 51 && true === e.AltKey && !e.AltGr) // Alt + Ctrl + Num3 - применяем стиль Heading3
    {
        if (false === this.Document_Is_SelectionLocked(AscCommon.changestype_Paragraph_Properties))
        {
            this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetStyleHeading3);
            this.SetParagraphStyle("Heading 3");
            this.Document_UpdateInterfaceState();
        }
        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode === 53 && true === e.CtrlKey) // Ctrl + Num5 - зачеркиваем текст
    {
        var TextPr = this.GetCalculatedTextPr();
        if (null != TextPr)
        {
            if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
            {
                this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextStrikeoutHotKey);
                this.AddToParagraph(new ParaTextPr({Strikeout : TextPr.Strikeout === true ? false : true}));
                this.Document_UpdateInterfaceState();
            }
            bRetValue = keydownresult_PreventAll;
        }
    }
    else if (e.KeyCode == 65 && true === e.CtrlKey) // Ctrl + A - выделяем все
    {
        this.SelectAll();
        bUpdateSelection = false;
        bRetValue        = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 66 && true === e.CtrlKey) // Ctrl + B - делаем текст жирным
    {
        var TextPr = this.GetCalculatedTextPr();
        if (null != TextPr)
        {
            if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
            {
                this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextBoldHotKey);
                this.AddToParagraph(new ParaTextPr({Bold : TextPr.Bold === true ? false : true}));
                this.Document_UpdateInterfaceState();
            }
            bRetValue = keydownresult_PreventAll;
        }
    }
    else if (e.KeyCode == 67 && true === e.CtrlKey) // Ctrl + C + ...
    {
        if (true === e.ShiftKey) // Ctrl + Shift + C - копирование форматирования текста
        {
            this.Document_Format_Copy();
            bRetValue = keydownresult_PreventAll;
        }
    }
    else if (e.KeyCode == 69 && true === e.CtrlKey) // Ctrl + E + ...
    {
        if (true !== e.AltKey) // Ctrl + E - переключение прилегания параграфа между center и left
        {
            this.private_ToggleParagraphAlignByHotkey(AscCommon.align_Center);
            bRetValue = keydownresult_PreventAll;
        }
        else // Ctrl + Alt + E - добавляем знак евро €
        {
            if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
            {
                this.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddEuroLetter);

                this.DrawingDocument.TargetStart();
                this.DrawingDocument.TargetShow();
                this.AddToParagraph(new ParaText("€"));
            }
            bRetValue = keydownresult_PreventAll;
        }
    }
	else if (e.KeyCode == 70 && true === e.CtrlKey) // Ctrl + F + ...
	{
		if (true === e.AltKey)
		{
			this.AddFootnote();
			bRetValue = keydownresult_PreventAll;
		}
	}
    else if (e.KeyCode == 73 && true === e.CtrlKey) // Ctrl + I - делаем текст наклонным
    {
        var TextPr = this.GetCalculatedTextPr();
        if (null != TextPr)
        {
            if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
            {
                this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextItalicHotKey);
                this.AddToParagraph(new ParaTextPr({Italic : TextPr.Italic === true ? false : true}));
                this.Document_UpdateInterfaceState();
            }
            bRetValue = keydownresult_PreventAll;
        }
    }
    else if (e.KeyCode == 74 && true === e.CtrlKey) // Ctrl + J переключение прилегания параграфа между justify и left
    {
        this.private_ToggleParagraphAlignByHotkey(AscCommon.align_Justify);
        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 75 && true === e.CtrlKey && false === e.ShiftKey) // Ctrl + K - добавление гиперссылки
    {
        if (true === this.CanAddHyperlink(false) && this.CanEdit())
            this.Api.sync_DialogAddHyperlink();

        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 76 && true === e.CtrlKey) // Ctrl + L + ...
    {
        if (true === e.ShiftKey) // Ctrl + Shift + L - добавляем список к данному параграфу
        {
            if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
            {
                this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetParagraphNumberingHotKey);
                this.SetParagraphNumbering({Type : 0, SubType : 1});
                this.Document_UpdateInterfaceState();
            }
            bRetValue = keydownresult_PreventAll;
        }
        else // Ctrl + L - переключение прилегания параграфа между left и justify
        {
            this.private_ToggleParagraphAlignByHotkey(align_Left);
            bRetValue = keydownresult_PreventAll;
        }
    }
    else if (e.KeyCode == 77 && true === e.CtrlKey) // Ctrl + M + ...
    {
        if (true === e.ShiftKey) // Ctrl + Shift + M - уменьшаем левый отступ
            this.DecreaseIndent();
        else // Ctrl + M - увеличиваем левый отступ
            this.IncreaseIndent();

        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 80 && true === e.CtrlKey) // Ctrl + P + ...
    {
        if (true === e.ShiftKey) // Ctrl + Shift + P - добавляем номер страницы в текущую позицию
        {
            if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
            {
                this.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddPageNumHotKey);
                this.AddToParagraph(new ParaPageNum());
            }
            bRetValue = keydownresult_PreventAll;
        }
        else // Ctrl + P - print
        {
            this.DrawingDocument.m_oWordControl.m_oApi.onPrint();
            bRetValue = keydownresult_PreventAll;
        }
    }
    else if (e.KeyCode == 82 && true === e.CtrlKey) // Ctrl + R - переключение прилегания параграфа между right и left
    {
        this.private_ToggleParagraphAlignByHotkey(AscCommon.align_Right);
        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 83 && false === this.IsViewMode() && true === e.CtrlKey) // Ctrl + S - save
    {
		this.Api.asc_Save(false);
        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 85 && true === e.CtrlKey) // Ctrl + U - делаем текст подчеркнутым
    {
        var TextPr = this.GetCalculatedTextPr();
        if (null != TextPr)
        {
            if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
            {
                this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextUnderlineHotKey);
                this.AddToParagraph(new ParaTextPr({Underline : TextPr.Underline === true ? false : true}));
                this.Document_UpdateInterfaceState();
            }
            bRetValue = keydownresult_PreventAll;
        }
    }
	else if (e.KeyCode == 86 && true === e.CtrlKey) // Ctrl + V
	{
		if (true === e.ShiftKey) // Ctrl + Shift + V - вставка форматирования текста
		{
			if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
			{
				this.Create_NewHistoryPoint(AscDFH.historydescription_Document_FormatPasteHotKey);
				this.Document_Format_Paste();
			}
			bRetValue = keydownresult_PreventAll;
		}
	}
    else if (e.KeyCode == 89 && true === e.CtrlKey && (this.CanEdit() || this.IsEditCommentsMode() || this.IsFillingFormMode())) // Ctrl + Y - Redo
    {
        this.Document_Redo();
        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 90 && true === e.CtrlKey && (this.CanEdit() || this.IsEditCommentsMode() || this.IsFillingFormMode())) // Ctrl + Z - Undo
    {
       	this.Document_Undo();
        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 93 || 57351 == e.KeyCode /*в Opera такой код*/) // контекстное меню
    {
        var X_abs, Y_abs, oPosition, ConvertedPos;
        if (this.DrawingObjects.selectedObjects.length > 0)
        {
            oPosition    = this.DrawingObjects.getContextMenuPosition(this.CurPage);
            ConvertedPos = this.DrawingDocument.ConvertCoordsToCursorWR(oPosition.X, oPosition.Y, oPosition.PageIndex);
        }
        else
        {
            ConvertedPos = this.DrawingDocument.ConvertCoordsToCursorWR(this.TargetPos.X, this.TargetPos.Y, this.TargetPos.PageNum);
        }
        X_abs = ConvertedPos.X;
        Y_abs = ConvertedPos.Y;

        editor.sync_ContextMenuCallback({Type : Asc.c_oAscContextMenuTypes.Common, X_abs : X_abs, Y_abs : Y_abs});

        bUpdateSelection = false;
        bRetValue        = keydownresult_PreventAll;
    }
	else if (e.KeyCode === 112 && true === e.CtrlKey)
	{
		// TODO: Добавлено для теста

		this.Create_NewHistoryPoint();
		this.AddField(fieldtype_TOC);
		this.Recalculate();

		bRetValue = keydownresult_PreventAll;
	}
    else if (e.KeyCode === 113 && true === e.CtrlKey)
	{
		// TODO: Добавлено для теста
		var arrFields = this.GetComplexFieldsByContentPos(this.GetContentPosition(false));
		if (arrFields && arrFields.length > 0)
			this.UpdateComplexField(arrFields[arrFields.length - 1]);

		bRetValue = keydownresult_PreventAll;
	}
	else if (e.KeyCode === 114 && true === e.CtrlKey)
	{
		this.Create_NewHistoryPoint();
		this.AddField(fieldtype_PAGEREF);
		this.Recalculate();

		bRetValue = keydownresult_PreventAll;
	}
	else if (e.KeyCode == 121 && true === e.ShiftKey) // Shift + F10 - контекстное меню
    {
        var X_abs, Y_abs, oPosition, ConvertedPos;
        if (this.DrawingObjects.selectedObjects.length > 0)
        {
            oPosition    = this.DrawingObjects.getContextMenuPosition(this.CurPage);
            ConvertedPos = this.DrawingDocument.ConvertCoordsToCursorWR(oPosition.X, oPosition.Y, oPosition.PageIndex);
        }
        else
        {
            ConvertedPos = this.DrawingDocument.ConvertCoordsToCursorWR(this.TargetPos.X, this.TargetPos.Y, this.TargetPos.PageNum);
        }
        X_abs = ConvertedPos.X;
        Y_abs = ConvertedPos.Y;

        editor.sync_ContextMenuCallback({Type : Asc.c_oAscContextMenuTypes.Common, X_abs : X_abs, Y_abs : Y_abs});

        bUpdateSelection = false;
        bRetValue        = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 144) // Num Lock
    {
        // Ничего не делаем
        bUpdateSelection = false;
        bRetValue        = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 145) // Scroll Lock
    {
        // Ничего не делаем
        bUpdateSelection = false;
        bRetValue        = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 187) // =
    {
        if (true === e.CtrlKey) // Ctrl + Shift + +, Ctrl + = - superscript/subscript
        {
            var TextPr = this.GetCalculatedTextPr();
            if (null != TextPr)
            {
                if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
                {
                    this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextVertAlignHotKey);
                    if (true === e.ShiftKey)
                        this.AddToParagraph(new ParaTextPr({VertAlign : TextPr.VertAlign === AscCommon.vertalign_SuperScript ? AscCommon.vertalign_Baseline : AscCommon.vertalign_SuperScript}));
                    else
                        this.AddToParagraph(new ParaTextPr({VertAlign : TextPr.VertAlign === AscCommon.vertalign_SubScript ? AscCommon.vertalign_Baseline : AscCommon.vertalign_SubScript}));
                    this.Document_UpdateInterfaceState();
                }
                bRetValue = keydownresult_PreventAll;
            }
        }
        else if (true === e.AltKey && !e.AltGr) // Alt + =
        {
            var oSelectedInfo = this.GetSelectedElementsInfo();
            var oMath         = oSelectedInfo.Get_Math();
            if (null === oMath)
            {
                if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
                {
                    this.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddMathHotKey);
                    this.AddToParagraph(new MathMenu(-1));
                    bRetValue = keydownresult_PreventAll;
                }
            }
        }
    }
    else if (e.KeyCode == 188 && true === e.CtrlKey) // Ctrl + ,
    {
        var TextPr = this.GetCalculatedTextPr();
        if (null != TextPr)
        {
            if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
            {
                this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextVertAlignHotKey2);
                this.AddToParagraph(new ParaTextPr({VertAlign : TextPr.VertAlign === AscCommon.vertalign_SuperScript ? AscCommon.vertalign_Baseline : AscCommon.vertalign_SuperScript}));
                this.Document_UpdateInterfaceState();
            }
            bRetValue = keydownresult_PreventAll;
        }
    }
    else if (e.KeyCode == 189) // Клавиша Num-
    {
        if (true === e.CtrlKey && true === e.ShiftKey && false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content, null, true))
        {
            this.Create_NewHistoryPoint(AscDFH.historydescription_Document_MinusButton);

            this.DrawingDocument.TargetStart();
            this.DrawingDocument.TargetShow();

            var Item = new ParaText(String.fromCharCode(0x2013));
            Item.Set_SpaceAfter(false);

            this.AddToParagraph(Item);
            bRetValue = keydownresult_PreventAll;
        }
    }
    else if (e.KeyCode == 190 && true === e.CtrlKey) // Ctrl + .
    {
        var TextPr = this.GetCalculatedTextPr();
        if (null != TextPr)
        {
            if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
            {
                this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextVertAlignHotKey3);
                this.AddToParagraph(new ParaTextPr({VertAlign : TextPr.VertAlign === AscCommon.vertalign_SubScript ? AscCommon.vertalign_Baseline : AscCommon.vertalign_SubScript}));
                this.Document_UpdateInterfaceState();
            }
            bRetValue = keydownresult_PreventAll;
        }
    }
    else if (e.KeyCode == 219 && true === e.CtrlKey) // Ctrl + [
    {
    	this.Api.FontSizeOut();
        this.Document_UpdateInterfaceState();
        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 221 && true === e.CtrlKey) // Ctrl + ]
    {
        this.Api.FontSizeIn();
        this.Document_UpdateInterfaceState();
        bRetValue = keydownresult_PreventAll;
    }
    else if (e.KeyCode == 12288) // Space
    {
        if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content, null, true, this.IsFormFieldEditing()))
        {
            this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SpaceButton);

            this.DrawingDocument.TargetStart();
            this.DrawingDocument.TargetShow();

            this.CheckLanguageOnTextAdd = true;
            this.AddToParagraph(new ParaSpace());
            this.CheckLanguageOnTextAdd = false;
        }

        bRetValue = keydownresult_PreventAll;
    }

    // Если был пересчет, значит были изменения, а вместе с ними пересылается и новая позиция курсора
    if (bRetValue & keydownresult_PreventKeyPress && OldRecalcId === this.RecalcId)
        this.private_UpdateTargetForCollaboration();

    if (bRetValue & keydownflags_PreventKeyPress && true === bUpdateSelection)
        this.Document_UpdateSelectionState();

    return bRetValue;
};
CDocument.prototype.OnKeyPress = function(e)
{
	var Code;
	if (null != e.Which)
		Code = e.Which;
	else if (e.KeyCode)
		Code = e.KeyCode;
	else
		Code = 0;//special char

	var bRetValue = false;

	if (Code > 0x20)
	{
		if (false === this.Document_Is_SelectionLocked(AscCommon.changestype_Paragraph_AddText, null, true, this.IsFormFieldEditing()))
		{
			this.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddLetter);

			this.DrawingDocument.TargetStart();
			this.DrawingDocument.TargetShow();

			this.CheckLanguageOnTextAdd = true;
			this.AddToParagraph(new ParaText(String.fromCharCode(Code)));
			this.CheckLanguageOnTextAdd = false;
		}
		bRetValue = true;
	}

	if (true == bRetValue)
		this.Document_UpdateSelectionState();

	return bRetValue;
};
CDocument.prototype.OnMouseDown = function(e, X, Y, PageIndex)
{
	if (PageIndex < 0)
		return;

	this.private_UpdateTargetForCollaboration();

	// Сбрасываем проверку Drag-n-Drop
	this.Selection.DragDrop.Flag = 0;
	this.Selection.DragDrop.Data = null;

	// Сбрасываем текущий элемент в поиске
	if (this.SearchEngine.Count > 0)
		this.SearchEngine.Reset_Current();

	// Обработка правой кнопки мыши происходит на событии MouseUp
	if (AscCommon.g_mouse_button_right === e.Button)
		return;

	// Если мы только что расширяли документ двойным щелчком, то отменяем это действие
	if (true === this.History.Is_ExtendDocumentToPos())
		this.Document_Undo();

	var OldCurPage = this.CurPage;
	this.CurPage   = PageIndex;

	if (true === editor.isStartAddShape && (docpostype_HdrFtr !== this.CurPos.Type || null !== this.HdrFtr.CurHdrFtr))
	{
		if (docpostype_HdrFtr !== this.CurPos.Type)
		{
			this.Set_DocPosType(docpostype_DrawingObjects);
			this.Selection.Use   = true;
			this.Selection.Start = true;
		}
		else
		{
			this.Selection.Use   = true;
			this.Selection.Start = true;

			this.HdrFtr.WaitMouseDown = false;
			var CurHdrFtr             = this.HdrFtr.CurHdrFtr;
			var DocContent            = CurHdrFtr.Content;

			DocContent.Set_DocPosType(docpostype_DrawingObjects);
			DocContent.Selection.Use   = true;
			DocContent.Selection.Start = true;
		}

		if (true != this.DrawingObjects.isPolylineAddition())
			this.DrawingObjects.startAddShape(editor.addShapePreset);

		this.DrawingObjects.OnMouseDown(e, X, Y, this.CurPage);
	}
	else
	{
		if (true === e.ShiftKey &&
			( (docpostype_DrawingObjects !== this.CurPos.Type && !(docpostype_HdrFtr === this.CurPos.Type && this.HdrFtr.CurHdrFtr && this.HdrFtr.CurHdrFtr.Content.CurPos.Type === docpostype_DrawingObjects))
			|| true === this.DrawingObjects.checkTextObject(X, Y, PageIndex) ))
		{
			if (true === this.IsSelectionUse())
				this.Selection.Start = false;
			else
				this.StartSelectionFromCurPos();

			this.Selection_SetEnd(X, Y, e);
			this.Document_UpdateSelectionState();
			return;
		}

		this.Selection_SetStart(X, Y, e);

		if (e.ClickCount <= 1 && 1 !== this.Selection.DragDrop.Flag)
		{
			this.RecalculateCurPos();
			this.Document_UpdateSelectionState();
		}
	}
};
CDocument.prototype.OnMouseUp = function(e, X, Y, PageIndex)
{
	if (PageIndex < 0)
		return;

	this.private_UpdateTargetForCollaboration();

	if (1 === this.Selection.DragDrop.Flag)
	{
		this.Selection.DragDrop.Flag = -1;
		var OldCurPage               = this.CurPage;
		this.CurPage                 = this.Selection.DragDrop.Data.PageNum;
		this.Selection_SetStart(this.Selection.DragDrop.Data.X, this.Selection.DragDrop.Data.Y, e);
		this.Selection.DragDrop.Flag = 0;
		this.Selection.DragDrop.Data = null;
	}

	// Если мы нажимали правую кнопку мыши, тогда нам надо сделать
	if (AscCommon.g_mouse_button_right === e.Button)
	{
		if (true === this.Selection.Start)
			return;

		var ConvertedPos = this.DrawingDocument.ConvertCoordsToCursorWR(X, Y, PageIndex);
		var X_abs        = ConvertedPos.X;
		var Y_abs        = ConvertedPos.Y;

		// Проверим попадание в значок таблицы, если в него попадаем, тогда выделяем таблицу
		if (true === this.DrawingDocument.IsCursorInTableCur(X, Y, PageIndex))
		{
			var Table = this.DrawingDocument.TableOutlineDr.TableOutline.Table;
			Table.SelectAll();
			Table.Document_SetThisElementCurrent(false);
			this.Document_UpdateSelectionState();
			this.Document_UpdateInterfaceState();
			editor.sync_ContextMenuCallback({Type : Asc.c_oAscContextMenuTypes.Common, X_abs : X_abs, Y_abs : Y_abs});
			return;
		}

		// Сначала проверим попадание в Flow-таблицы и автофигуры
		var pFlowTable = this.DrawingObjects.getTableByXY(X, Y, PageIndex, this);
		var nInDrawing = this.DrawingObjects.IsInDrawingObject(X, Y, PageIndex, this);

		if (docpostype_HdrFtr != this.CurPos.Type && -1 === nInDrawing && null === pFlowTable)
		{
			var PageMetrics = this.Get_PageContentStartPos(this.CurPage, this.Pages[this.CurPage].Pos);
			// Проверяем, не попали ли мы в колонтитул
			if (Y <= PageMetrics.Y)
			{
				editor.sync_ContextMenuCallback({
					Type    : Asc.c_oAscContextMenuTypes.ChangeHdrFtr,
					X_abs   : X_abs,
					Y_abs   : Y_abs,
					Header  : true,
					PageNum : PageIndex
				});
				return;
			}
			else if (Y > PageMetrics.YLimit)
			{
				editor.sync_ContextMenuCallback({
					Type    : Asc.c_oAscContextMenuTypes.ChangeHdrFtr,
					X_abs   : X_abs,
					Y_abs   : Y_abs,
					Header  : false,
					PageNum : PageIndex
				});
				return;
			}
		}

		// Проверяем попалили мы в селект
		if (false === this.CheckPosInSelection(X, Y, PageIndex, undefined))
		{
			this.CurPage = PageIndex;

			var MouseEvent_new =
				{
					// TODO : Если в MouseEvent будет использоваться что-то кроме ClickCount, Type и CtrlKey, добавить здесь
					ClickCount : 1,
					Type       : AscCommon.g_mouse_event_type_down,
					CtrlKey    : false,
					Button     : AscCommon.g_mouse_button_right
				};
			this.Selection_SetStart(X, Y, MouseEvent_new);

			MouseEvent_new.Type = AscCommon.g_mouse_event_type_up;
			this.Selection_SetEnd(X, Y, MouseEvent_new);

			this.Document_UpdateSelectionState();
			this.Document_UpdateRulersState();
			this.Document_UpdateInterfaceState();
		}

		editor.sync_ContextMenuCallback({Type : Asc.c_oAscContextMenuTypes.Common, X_abs : X_abs, Y_abs : Y_abs});
		this.private_UpdateCursorXY(true, true);

		return;
	}
	else if (AscCommon.g_mouse_button_left === e.Button)
	{
		if (true === this.Comments.Is_Use())
		{
			var Type    = ( docpostype_HdrFtr === this.CurPos.Type ? comment_type_HdrFtr : comment_type_Common );
			// Проверяем не попали ли мы в комментарий
			var Comment = this.Comments.Get_ByXY(PageIndex, X, Y, Type);
			if (null != Comment && (this.Comments.IsUseSolved() || !Comment.IsSolved()))
			{
				var Comment_PageNum = Comment.m_oStartInfo.PageNum;
				var Comment_Y       = Comment.m_oStartInfo.Y;
				var Comment_X       = this.Get_PageLimits(PageIndex).XLimit;
				var Para            = g_oTableId.Get_ById(Comment.StartId);

				if (!Para)
				{
					// Такое может быть, если комментарий добавлен к заголовку таблицы
					this.SelectComment(null, false);
					editor.sync_HideComment();
				}
				else
				{
					var TextTransform = Para.Get_ParentTextTransform();
					if (TextTransform)
					{
						Comment_Y = TextTransform.TransformPointY(Comment.m_oStartInfo.X, Comment.m_oStartInfo.Y);
					}

					var Coords = this.DrawingDocument.ConvertCoordsToCursorWR(Comment_X, Comment_Y, Comment_PageNum);
					this.SelectComment(Comment.Get_Id(), false);
					editor.sync_ShowComment(Comment.Get_Id(), Coords.X, Coords.Y);
				}
			}
			else
			{
				this.SelectComment(null, false);
				editor.sync_HideComment();
			}
		}
	}

	if (true === this.Selection.Start)
	{
		this.CurPage         = PageIndex;
		this.Selection.Start = false;
		this.Selection_SetEnd(X, Y, e);
		this.CheckComplexFieldsInSelection();
		this.Document_UpdateSelectionState();

		if (c_oAscFormatPainterState.kOff !== editor.isPaintFormat)
		{
			if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
			{
				this.Create_NewHistoryPoint(AscDFH.historydescription_Document_FormatPasteHotKey2);
				this.Document_Format_Paste();
			}

			if (c_oAscFormatPainterState.kOn === editor.isPaintFormat)
				editor.sync_PaintFormatCallback(c_oAscFormatPainterState.kOff);
		}
		else if (true === editor.isMarkerFormat && true === this.IsTextSelectionUse())
		{
			if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
			{
				this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextHighlight2);
				var ParaItem = null;
				if (this.HighlightColor != highlight_None)
				{
					var TextPr = this.GetCalculatedTextPr();
					if ("undefined" === typeof( TextPr.HighLight ) || null === TextPr.HighLight || highlight_None === TextPr.HighLight ||
						this.HighlightColor.r != TextPr.HighLight.r || this.HighlightColor.g != TextPr.HighLight.g || this.HighlightColor.b != TextPr.HighLight.b)
						ParaItem = new ParaTextPr({HighLight : this.HighlightColor});
					else
						ParaItem = new ParaTextPr({HighLight : highlight_None});
				}
				else
					ParaItem = new ParaTextPr({HighLight : this.HighlightColor});

				this.AddToParagraph(ParaItem);
				this.MoveCursorToXY(X, Y, false);
				this.Document_UpdateSelectionState();

				editor.sync_MarkerFormatCallback(true);
			}
		}
	}

	this.private_CheckCursorPosInFillingFormMode();

	this.private_UpdateCursorXY(true, true);
};
CDocument.prototype.OnMouseMove = function(e, X, Y, PageIndex)
{
	if (PageIndex < 0)
		return;

	if (true === this.Selection.Start)
		this.private_UpdateTargetForCollaboration();

	this.UpdateCursorType(X, Y, PageIndex, e);
	this.CollaborativeEditing.Check_ForeignCursorsLabels(X, Y, PageIndex);

	if (1 === this.Selection.DragDrop.Flag)
	{
		// Если курсор не изменил позицию, тогда ничего не делаем, а если изменил, тогда стартуем Drag-n-Drop
		if (Math.abs(this.Selection.DragDrop.Data.X - X) > 0.001 || Math.abs(this.Selection.DragDrop.Data.Y - Y) > 0.001)
		{
			this.Selection.DragDrop.Flag = 0;
			this.Selection.DragDrop.Data = null;

			// Вызываем стандартное событие mouseMove, чтобы сбросить различные подсказки, если они были
			this.Api.sync_MouseMoveStartCallback();
			this.Api.sync_MouseMoveCallback(new AscCommon.CMouseMoveData());
			this.Api.sync_MouseMoveEndCallback();

			this.DrawingDocument.StartTrackText();
		}

		return;
	}

	if (true === this.Selection.Use && true === this.Selection.Start)
	{
		this.CurPage = PageIndex;
		this.Selection_SetEnd(X, Y, e);
		this.Document_UpdateSelectionState();
	}
};
CDocument.prototype.Get_Numbering = function()
{
	return this.Numbering;
};
CDocument.prototype.Internal_GetNumInfo = function(ParaId, NumPr)
{
	var TopDocument = this.Get_TopDocumentContent();
	return TopDocument.GetNumberingInfo(null, ParaId, NumPr);
};
CDocument.prototype.Get_Styles = function()
{
	return this.Styles;
};
CDocument.prototype.CopyStyle = function()
{
	return this.Styles.CopyStyle();
};
CDocument.prototype.Get_TableStyleForPara = function()
{
	return null;
};
CDocument.prototype.Get_ShapeStyleForPara = function()
{
	return null;
};
CDocument.prototype.Get_TextBackGroundColor = function()
{
	return undefined;
};
CDocument.prototype.Select_DrawingObject = function(Id)
{
	this.RemoveSelection();

	// Прячем курсор
	this.DrawingDocument.TargetEnd();
	this.DrawingDocument.SetCurrentPage(this.CurPage);

	this.Selection.Start = false;
	this.Selection.Use   = true;
	this.Set_DocPosType(docpostype_DrawingObjects);
	this.DrawingObjects.selectById(Id, this.CurPage);

	this.Document_UpdateInterfaceState();
	this.Document_UpdateSelectionState();
};
/**
 * Получем ближайшую возможную позицию курсора.
 * @param PageNum
 * @param X
 * @param Y
 * @param bAnchor
 * @param Drawing
 * @returns {*}
 */
CDocument.prototype.Get_NearestPos = function(PageNum, X, Y, bAnchor, Drawing)
{
	if (undefined === bAnchor)
		bAnchor = false;

	if (docpostype_HdrFtr === this.Get_DocPosType())
		return this.HdrFtr.Get_NearestPos(PageNum, X, Y, bAnchor, Drawing);

	var bInText    = (null === this.IsInText(X, Y, PageNum) ? false : true);
	var nInDrawing = this.DrawingObjects.IsInDrawingObject(X, Y, PageNum, this);

	if (true != bAnchor)
	{
		// Проверяем попадание в графические объекты
		var NearestPos = this.DrawingObjects.getNearestPos(X, Y, PageNum, Drawing);
		if (( nInDrawing === DRAWING_ARRAY_TYPE_BEFORE || nInDrawing === DRAWING_ARRAY_TYPE_INLINE || ( false === bInText && nInDrawing >= 0 ) ) && null != NearestPos)
			return NearestPos;

		NearestPos = true === this.Footnotes.CheckHitInFootnote(X, Y, PageNum) ? this.Footnotes.GetNearestPos(X, Y, PageNum, false, Drawing) : null;
		if (null !== NearestPos)
			return NearestPos;
	}

	var ContentPos = this.Internal_GetContentPosByXY(X, Y, PageNum);

	// Делаем логику как в ворде
	if (true === bAnchor && ContentPos > 0 && PageNum > 0 && ContentPos === this.Pages[PageNum].Pos && ContentPos === this.Pages[PageNum - 1].EndPos && this.Pages[PageNum].EndPos > this.Pages[PageNum].Pos && type_Paragraph === this.Content[ContentPos].GetType() && true === this.Content[ContentPos].IsContentOnFirstPage())
		ContentPos++;

	var ElementPageIndex = this.private_GetElementPageIndexByXY(ContentPos, X, Y, PageNum);
	return this.Content[ContentPos].GetNearestPos(ElementPageIndex, X, Y, bAnchor, Drawing);
};
CDocument.prototype.Internal_Content_Add = function(Position, NewObject, bCheckLastElement)
{
	// Position = this.Content.length  допускается
	if (Position < 0 || Position > this.Content.length)
		return;

	var PrevObj = this.Content[Position - 1] ? this.Content[Position - 1] : null;
	var NextObj = this.Content[Position] ? this.Content[Position] : null;

	this.private_RecalculateNumbering([NewObject]);
	this.History.Add(new CChangesDocumentAddItem(this, Position, [NewObject]));
	this.Content.splice(Position, 0, NewObject);
	NewObject.Set_Parent(this);
	NewObject.Set_DocumentNext(NextObj);
	NewObject.Set_DocumentPrev(PrevObj);

	if (null != PrevObj)
		PrevObj.Set_DocumentNext(NewObject);

	if (null != NextObj)
		NextObj.Set_DocumentPrev(NewObject);

	// Обновим информацию о секциях
	this.SectionsInfo.Update_OnAdd(Position, [NewObject]);

	// Проверим последний параграф
	this.Check_SectionLastParagraph();

	// Проверим, что последний элемент - параграф
	if (false !== bCheckLastElement && type_Paragraph !== this.Content[this.Content.length - 1].GetType())
		this.Internal_Content_Add(this.Content.length, new Paragraph(this.DrawingDocument, this));

	// Запоминаем, что нам нужно произвести переиндексацию элементов
	this.private_ReindexContent(Position);
};
CDocument.prototype.Internal_Content_Remove = function(Position, Count, bCheckLastElement)
{
	var ChangePos = -1;

	if (Position < 0 || Position >= this.Content.length || Count <= 0)
		return -1;

	var PrevObj = this.Content[Position - 1] ? this.Content[Position - 1] : null;
	var NextObj = this.Content[Position + Count] ? this.Content[Position + Count] : null;

	for (var Index = 0; Index < Count; Index++)
	{
		this.Content[Position + Index].PreDelete();
	}

	this.History.Add(new CChangesDocumentRemoveItem(this, Position, this.Content.slice(Position, Position + Count)));
	var Elements = this.Content.splice(Position, Count);
	this.private_RecalculateNumbering(Elements);

	if (null != PrevObj)
		PrevObj.Set_DocumentNext(NextObj);

	if (null != NextObj)
		NextObj.Set_DocumentPrev(PrevObj);

	// Проверим, что последний элемент - параграф
	if (false !== bCheckLastElement && (this.Content.length <= 0 || type_Paragraph !== this.Content[this.Content.length - 1].GetType()))
		this.Internal_Content_Add(this.Content.length, new Paragraph(this.DrawingDocument, this));

	// Обновим информацию о секциях
	this.SectionsInfo.Update_OnRemove(Position, Count, true);

	// Проверим последний параграф
	this.Check_SectionLastParagraph();

	// Проверим не является ли рамкой последний параграф
	this.private_CheckFramePrLastParagraph();

	// Запоминаем, что нам нужно произвести переиндексацию элементов
	this.private_ReindexContent(Position);

	return ChangePos;
};
CDocument.prototype.Clear_ContentChanges = function()
{
	this.m_oContentChanges.Clear();
};
CDocument.prototype.Add_ContentChanges = function(Changes)
{
	this.m_oContentChanges.Add(Changes);
};
CDocument.prototype.Refresh_ContentChanges = function()
{
	this.m_oContentChanges.Refresh();
};
/**
 * @param AlignV 0 - Верх, 1 - низ
 * @param AlignH стандартные значения align_Left, align_Center, align_Right
 */
CDocument.prototype.Document_AddPageNum = function(AlignV, AlignH)
{
	if (AlignV >= 0)
	{
		var PageIndex = this.CurPage;
		if (docpostype_HdrFtr === this.Get_DocPosType())
			PageIndex = this.HdrFtr.Get_CurPage();

		if (PageIndex < 0)
			PageIndex = this.CurPage;

		this.Create_HdrFtrWidthPageNum(PageIndex, AlignV, AlignH);
	}
	else
	{
		this.AddToParagraph(new ParaPageNum());
	}

	this.Document_UpdateInterfaceState();
};
CDocument.prototype.Document_SetHdrFtrFirstPage = function(Value)
{
	var CurHdrFtr = this.HdrFtr.CurHdrFtr;

	if (null === CurHdrFtr || -1 === CurHdrFtr.RecalcInfo.CurPage)
		return;

	var CurPage = CurHdrFtr.RecalcInfo.CurPage;
	var Index   = this.Pages[CurPage].Pos;
	var SectPr  = this.SectionsInfo.Get_SectPr(Index).SectPr;

	SectPr.Set_TitlePage(Value);

	if (true === Value)
	{
		// Если мы добавляем разные колонтитулы для первой страницы, а этих колонтитулов нет, тогда создаем их
		var FirstSectPr = this.SectionsInfo.Get_SectPr2(0).SectPr;
		var FirstHeader = FirstSectPr.Get_Header_First();
		var FirstFooter = FirstSectPr.Get_Footer_First();

		if (null === FirstHeader)
		{
			var Header = new CHeaderFooter(this.HdrFtr, this, this.DrawingDocument, hdrftr_Header);
			FirstSectPr.Set_Header_First(Header);

			this.HdrFtr.Set_CurHdrFtr(Header);
		}
		else
			this.HdrFtr.Set_CurHdrFtr(FirstHeader);

		if (null === FirstFooter)
		{
			var Footer = new CHeaderFooter(this.HdrFtr, this, this.DrawingDocument, hdrftr_Footer);
			FirstSectPr.Set_Footer_First(Footer);
		}
	}
	else
	{
		var TempSectPr = SectPr;
		var TempIndex  = Index;
		while (null === TempSectPr.Get_Header_Default())
		{
			TempIndex--;
			if (TempIndex < 0)
				break;

			TempSectPr = this.SectionsInfo.Get_SectPr(TempIndex).SectPr;
		}

		this.HdrFtr.Set_CurHdrFtr(TempSectPr.Get_Header_Default());
	}

	if (null !== this.HdrFtr.CurHdrFtr)
		this.HdrFtr.CurHdrFtr.Content.MoveCursorToStartPos();

	this.Recalculate();

	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.Document_SetHdrFtrEvenAndOddHeaders = function(Value)
{
	this.Set_DocumentEvenAndOddHeaders(Value);

	var FirstSectPr;
	if (true === Value)
	{
		// Если мы добавляем разные колонтитулы для четных и нечетных страниц, а этих колонтитулов нет, тогда
		// создаем их в самой первой секции
		FirstSectPr = this.SectionsInfo.Get_SectPr2(0).SectPr;
		if (null === FirstSectPr.Get_Header_Even())
		{
			var Header = new CHeaderFooter(this.HdrFtr, this, this.DrawingDocument, hdrftr_Header);
			FirstSectPr.Set_Header_Even(Header);
		}

		if (null === FirstSectPr.Get_Footer_Even())
		{
			var Footer = new CHeaderFooter(this.HdrFtr, this, this.DrawingDocument, hdrftr_Footer);
			FirstSectPr.Set_Footer_Even(Footer);
		}
	}
	else
	{
		FirstSectPr = this.SectionsInfo.Get_SectPr2(0).SectPr;
	}

	if (null !== FirstSectPr.Get_Header_First() && true === FirstSectPr.TitlePage)
		this.HdrFtr.Set_CurHdrFtr(FirstSectPr.Get_Header_First());
	else
		this.HdrFtr.Set_CurHdrFtr(FirstSectPr.Get_Header_Default());


	this.Recalculate();

	if (null !== this.HdrFtr.CurHdrFtr)
		this.HdrFtr.CurHdrFtr.Content.MoveCursorToStartPos();

	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.Document_SetHdrFtrDistance = function(Value)
{
	var CurHdrFtr = this.HdrFtr.CurHdrFtr;

	if (null === CurHdrFtr)
		return;

	var CurPage = CurHdrFtr.RecalcInfo.CurPage;
	if (-1 === CurPage)
		return;

	var Index  = this.Pages[CurPage].Pos;
	var SectPr = this.SectionsInfo.Get_SectPr(Index).SectPr;

	if (hdrftr_Header === CurHdrFtr.Type)
		SectPr.Set_PageMargins_Header(Value);
	else
		SectPr.Set_PageMargins_Footer(Value);

	this.Recalculate();

	this.Document_UpdateRulersState();
	this.Document_UpdateInterfaceState();
	this.Document_UpdateSelectionState();
};
CDocument.prototype.Document_SetHdrFtrBounds = function(Y0, Y1)
{
	var CurHdrFtr = this.HdrFtr.CurHdrFtr;

	if (null === CurHdrFtr)
		return;

	var CurPage = CurHdrFtr.RecalcInfo.CurPage;
	if (-1 === CurPage)
		return;

	var Index  = this.Pages[CurPage].Pos;
	var SectPr = this.SectionsInfo.Get_SectPr(Index).SectPr;
	var Bounds = CurHdrFtr.Get_Bounds();

	if (hdrftr_Header === CurHdrFtr.Type)
	{
		if (null !== Y0)
			SectPr.Set_PageMargins_Header(Y0);

		if (null !== Y1)
			SectPr.Set_PageMargins(undefined, Y1, undefined, undefined);
	}
	else
	{
		if (null !== Y0)
		{
			var H   = Bounds.Bottom - Bounds.Top;
			var _Y1 = Y0 + H;

			SectPr.Set_PageMargins_Footer(SectPr.Get_PageHeight() - _Y1);
		}
	}

	this.Recalculate();

	this.Document_UpdateRulersState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.Document_SetHdrFtrLink = function(bLinkToPrevious)
{
	var CurHdrFtr = this.HdrFtr.CurHdrFtr;
	if (docpostype_HdrFtr !== this.Get_DocPosType() || null === CurHdrFtr || -1 === CurHdrFtr.RecalcInfo.CurPage)
		return;

	var PageIndex = CurHdrFtr.RecalcInfo.CurPage;

	var Index  = this.Pages[PageIndex].Pos;
	var SectPr = this.SectionsInfo.Get_SectPr(Index).SectPr;

	// У самой первой секции не может быть повторяющихся колонтитулов, поэтому не делаем ничего
	if (SectPr === this.SectionsInfo.Get_SectPr2(0).SectPr)
		return;

	// Определим тип колонтитула, в котором мы находимся
	var SectionPageInfo = this.Get_SectionPageNumInfo(PageIndex);

	var bFirst  = ( true === SectionPageInfo.bFirst && true === SectPr.Get_TitlePage() ? true : false );
	var bEven   = ( true === SectionPageInfo.bEven && true === EvenAndOddHeaders ? true : false );
	var bHeader = ( hdrftr_Header === CurHdrFtr.Type ? true : false );

	var _CurHdrFtr = SectPr.Get_HdrFtr(bHeader, bFirst, bEven);

	if (true === bLinkToPrevious)
	{
		// Если нам надо повторять колонтитул, а он уже изначально повторяющийся, тогда не делаем ничего
		if (null === _CurHdrFtr)
			return;

		// Очистим селект
		_CurHdrFtr.RemoveSelection();

		// Просто удаляем запись о данном колонтитуле в секции
		SectPr.Set_HdrFtr(bHeader, bFirst, bEven, null);

		var HdrFtr = this.Get_SectionHdrFtr(PageIndex, bFirst, bEven);

		// Заглушка. Вообще такого не должно быть, чтобы был колонтитул не в первой секции, и не было в первой,
		// но, на всякий случай, обработаем такую ситуацию.
		if (true === bHeader)
		{
			if (null === HdrFtr.Header)
				CurHdrFtr = this.Create_SectionHdrFtr(hdrftr_Header, PageIndex);
			else
				CurHdrFtr = HdrFtr.Header;
		}
		else
		{
			if (null === HdrFtr.Footer)
				CurHdrFtr = this.Create_SectionHdrFtr(hdrftr_Footer, PageIndex);
			else
				CurHdrFtr = HdrFtr.Footer;
		}


		this.HdrFtr.Set_CurHdrFtr(CurHdrFtr);
		this.HdrFtr.CurHdrFtr.MoveCursorToStartPos(false);
	}
	else
	{
		// Если данный колонтитул уже не повторяющийся, тогда ничего не делаем
		if (null !== _CurHdrFtr)
			return;

		var NewHdrFtr = CurHdrFtr.Copy();
		SectPr.Set_HdrFtr(bHeader, bFirst, bEven, NewHdrFtr);
		this.HdrFtr.Set_CurHdrFtr(NewHdrFtr);
		this.HdrFtr.CurHdrFtr.MoveCursorToStartPos(false);
	}

	this.Recalculate();

	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.Document_Format_Copy = function()
{
	this.CopyTextPr = this.GetDirectTextPr();
	this.CopyParaPr = this.GetDirectParaPr();
};
CDocument.prototype.EndHdrFtrEditing = function(bCanStayOnPage)
{
	if (docpostype_HdrFtr === this.Get_DocPosType())
	{
		this.Set_DocPosType(docpostype_Content);
		var CurHdrFtr = this.HdrFtr.Get_CurHdrFtr();
		if (null === CurHdrFtr || undefined === CurHdrFtr || true !== bCanStayOnPage)
		{
			this.MoveCursorToStartPos(false);
		}
		else
		{
			CurHdrFtr.RemoveSelection();

			if (hdrftr_Header == CurHdrFtr.Type)
				this.MoveCursorToXY(0, 0, false);
			else
				this.MoveCursorToXY(0, 100000, false); // TODO: Переделать здесь по-нормальному
		}

		this.DrawingDocument.ClearCachePages();
		this.DrawingDocument.FirePaint();

		this.Document_UpdateRulersState();
		this.Document_UpdateInterfaceState();
		this.Document_UpdateSelectionState();
	}
};
CDocument.prototype.EndFootnotesEditing = function()
{
	if (docpostype_Footnotes === this.Get_DocPosType())
	{
		this.Set_DocPosType(docpostype_Content);

		this.MoveCursorToStartPos(false);

		// TODO: Не всегда можно в данной функции использовать MoveCursorToXY, потому что
		//       данная страница еще может быть не рассчитана.
		//this.MoveCursorToXY(0, 0, false);

		this.DrawingDocument.ClearCachePages();
		this.DrawingDocument.FirePaint();

		this.Document_UpdateRulersState();
		this.Document_UpdateInterfaceState();
		this.Document_UpdateSelectionState();
	}
};
CDocument.prototype.EndDrawingEditing = function()
{
	if (docpostype_DrawingObjects === this.Get_DocPosType() || (docpostype_HdrFtr === this.Get_DocPosType() && null != this.HdrFtr.CurHdrFtr && docpostype_DrawingObjects === this.HdrFtr.CurHdrFtr.Content.CurPos.Type ))
	{
		this.DrawingObjects.resetSelection2();
		this.Document_UpdateInterfaceState();
		this.Document_UpdateSelectionState();
		this.private_UpdateCursorXY(true, true);
	}
};
CDocument.prototype.Document_Format_Paste = function()
{
	this.Controller.PasteFormatting(this.CopyTextPr, this.CopyParaPr);
	this.Recalculate();
	this.Document_UpdateInterfaceState();
	this.Document_UpdateSelectionState();
};
CDocument.prototype.IsTableCellContent = function(isReturnCell)
{
	if (true === isReturnCell)
		return null;

	return false;
};
CDocument.prototype.Check_AutoFit = function()
{
	return false;
};
CDocument.prototype.Is_TopDocument = function(bReturnTopDocument)
{
	if (true === bReturnTopDocument)
		return this;

	return true;
};
CDocument.prototype.Is_InTable = function(bReturnTopTable)
{
	if (true === bReturnTopTable)
		return null;

	return false;
};
CDocument.prototype.Is_DrawingShape = function(bRetShape)
{
	if (bRetShape === true)
	{
		return null;
	}
	return false;
};
CDocument.prototype.Is_HdrFtr = function(bReturnHdrFtr)
{
	if (true === bReturnHdrFtr)
		return null;

	return false;
};
CDocument.prototype.IsSelectionUse = function()
{
	return this.Controller.IsSelectionUse();
};
CDocument.prototype.IsTextSelectionUse = function()
{
	return this.Controller.IsTextSelectionUse();
};
CDocument.prototype.GetCurPosXY = function()
{
	var TempXY = this.Controller.GetCurPosXY();
	this.private_CheckCurPage();
	return {X : TempXY.X, Y : TempXY.Y, PageNum : this.CurPage};
};
/**
 * Возвращаем выделенный текст, если в выделении не более 1 параграфа, и там нет картинок, нумерации страниц и т.д.
 * @param bClearText
 * @param oPr
 * @returns {?string}
 */
CDocument.prototype.GetSelectedText = function(bClearText, oPr)
{
	if (undefined === oPr)
		oPr = {};

	if (undefined === bClearText)
		bClearText = false;

	return this.Controller.GetSelectedText(bClearText, oPr);
};
/**
 * Получаем текущий параграф (или граничные параграфы селекта)
 * @param bIgnoreSelection Если true, тогда используется текущая позиция, даже если есть селект
 * @param bReturnSelectedArray (Используется, только если bIgnoreSelection==false) Если true, тогда возвращаем массив из
 * из параграфов, которые попали в выделение.
 * @returns {Paragraph | [Paragraph]}
 */
CDocument.prototype.GetCurrentParagraph = function(bIgnoreSelection, bReturnSelectedArray)
{
	if (true !== bIgnoreSelection && true === bReturnSelectedArray)
	{
		var arrSelectedParagraphs = [];
		this.Controller.GetCurrentParagraph(bIgnoreSelection, arrSelectedParagraphs);
		return arrSelectedParagraphs;
	}
	else
	{
		return this.Controller.GetCurrentParagraph(bIgnoreSelection, null);
	}
};
CDocument.prototype.GetSelectedElementsInfo = function()
{
	var oInfo = new CSelectedElementsInfo();
	this.Controller.GetSelectedElementsInfo(oInfo);
	return oInfo;
};
//----------------------------------------------------------------------------------------------------------------------
// Функции для работы с таблицами
//----------------------------------------------------------------------------------------------------------------------
CDocument.prototype.AddTableRow = function(bBefore)
{
	this.Controller.AddTableRow(bBefore);
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.AddTableColumn = function(bBefore)
{
	this.Controller.AddTableColumn(bBefore);
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.RemoveTableRow = function()
{
	this.Controller.RemoveTableRow();
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.RemoveTableColumn = function()
{
	this.Controller.RemoveTableColumn();
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.MergeTableCells = function()
{
	this.Controller.MergeTableCells();
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.SplitTableCells = function(Cols, Rows)
{
	this.Controller.SplitTableCells(Cols, Rows);
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.RemoveTable = function()
{
	this.Controller.RemoveTable();
	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
	this.Document_UpdateRulersState();
};
CDocument.prototype.SelectTable = function(Type)
{
	this.Controller.SelectTable(Type);
	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
	//this.Document_UpdateRulersState();
};
CDocument.prototype.CanMergeTableCells = function()
{
	return this.Controller.CanMergeTableCells();
};
CDocument.prototype.CanSplitTableCells = function()
{
	return this.Controller.CanSplitTableCells();
};
CDocument.prototype.CheckTableCoincidence = function(Table)
{
	return false;
};
//----------------------------------------------------------------------------------------------------------------------
// Дополнительные функции
//----------------------------------------------------------------------------------------------------------------------
CDocument.prototype.Document_CreateFontMap = function()
{
	var FontMap = {};
	this.SectionsInfo.Document_CreateFontMap(FontMap);

	var Count = this.Content.length;
	for (var Index = 0; Index < Count; Index++)
	{
		this.Content[Index].CreateFontMap(FontMap);
	}
	AscFormat.checkThemeFonts(FontMap, this.theme.themeElements.fontScheme);
	return FontMap;
};
CDocument.prototype.Document_CreateFontCharMap = function(FontCharMap)
{
	this.SectionsInfo.Document_CreateFontCharMap(FontCharMap);
	this.DrawingObjects.documentCreateFontCharMap(FontCharMap);

	var Count = this.Content.length;
	for (var Index = 0; Index < Count; Index++)
	{
		this.Content[Index].CreateFontCharMap(FontCharMap);
	}
};
CDocument.prototype.Document_Get_AllFontNames = function()
{
	var AllFonts = {};

	this.SectionsInfo.Document_Get_AllFontNames(AllFonts);
	this.Numbering.Document_Get_AllFontNames(AllFonts);
	this.Styles.Document_Get_AllFontNames(AllFonts);
	this.theme.Document_Get_AllFontNames(AllFonts);

	for (var nIndex = 0, nCount = this.Content.length; nIndex < nCount; ++nIndex)
	{
		this.Content[nIndex].GetAllFontNames(AllFonts);
	}
	AscFormat.checkThemeFonts(AllFonts, this.theme.themeElements.fontScheme);
	return AllFonts;
};
/**
 * Обновляем текущее состояние (определяем где мы находимся, картинка/параграф/таблица/колонтитул)
 * @param bSaveCurRevisionChange
 */
CDocument.prototype.Document_UpdateInterfaceState = function(bSaveCurRevisionChange)
{
	if (true === this.TurnOffInterfaceEvents)
		return;

	if (true === AscCommon.CollaborativeEditing.Get_GlobalLockSelection())
		return;

	// Удаляем весь список
	this.Api.sync_BeginCatchSelectedElements();

	this.TrackRevisionsManager.Begin_CollectChanges(bSaveCurRevisionChange);

	// Уберем из интерфейса записи о том где мы находимся (параграф, таблица, картинка или колонтитул)
	this.Api.ClearPropObjCallback();

	this.Controller.UpdateInterfaceState();
	this.TrackRevisionsManager.End_CollectChanges(this.Api);

	// Сообщаем, что список составлен
	this.Api.sync_EndCatchSelectedElements();

	this.Document_UpdateUndoRedoState();
	this.Document_UpdateCanAddHyperlinkState();
	this.Document_UpdateSectionPr();
	this.Document_UpdateStylesPanel();
};
CDocument.prototype.Document_UpdateRulersState = function()
{
	if (true === this.TurnOffInterfaceEvents)
		return;

	if (true === AscCommon.CollaborativeEditing.Get_GlobalLockSelection())
		return;

	this.DrawingDocument.Set_RulerState_Start();
	this.Controller.UpdateRulersState();
	this.DrawingDocument.Set_RulerState_End();
};
CDocument.prototype.Document_UpdateRulersStateBySection = function(Pos)
{
	// В данной функции мы уже точно знаем, что нам секцию нужно выбирать исходя из текущего параграфа
	var CurPos = undefined === Pos ? ( this.Selection.Use === true ? this.Selection.EndPos : this.CurPos.ContentPos ) : Pos;

	var SectPr = this.SectionsInfo.Get_SectPr(CurPos).SectPr;

	var L = SectPr.Get_PageMargin_Left();
	var T = SectPr.Get_PageMargin_Top();
	var R = SectPr.Get_PageWidth() - SectPr.Get_PageMargin_Right();
	var B = SectPr.Get_PageHeight() - SectPr.Get_PageMargin_Bottom();

	var ColumnsCount = SectPr.Get_ColumnsCount();

	if (ColumnsCount > 1)
	{
		this.ColumnsMarkup.Update_FromSectPr(SectPr);

		var Element = this.Content[CurPos];
		if (type_Paragraph === Element.Get_Type())
			this.ColumnsMarkup.Set_CurCol(Element.Get_CurrentColumn());

		this.DrawingDocument.Set_RulerState_Columns(this.ColumnsMarkup);
	}
	else
	{
		this.DrawingDocument.Set_RulerState_Paragraph({L : L, T : T, R : R, B : B}, true);
	}
};
CDocument.prototype.Document_UpdateSelectionState = function()
{
	if (true === this.TurnOffInterfaceEvents)
		return;

	if (true === AscCommon.CollaborativeEditing.Get_GlobalLockSelection())
		return;

	this.DrawingDocument.UpdateTargetTransform(null);

	// TODO: Надо подумать как это вынести в верхнюю функцию внутренние реализации типа controller_UpdateSelectionState
	//       потому что они все очень похожие.

	this.Controller.UpdateSelectionState();

	// Обновим состояние кнопок Copy/Cut
	this.Document_UpdateCopyCutState();
};
CDocument.prototype.Document_UpdateTracks = function()
{
	this.private_UpdateTracks(this.IsSelectionUse(), this.IsSelectionEmpty());
};
CDocument.prototype.private_UpdateTracks = function(bSelection, bEmptySelection)
{
	var Pos = (true === this.Selection.Use && selectionflag_Numbering !== this.Selection.Flag ? this.Selection.EndPos : this.CurPos.ContentPos);
	if (docpostype_Content === this.Get_DocPosType() && !(Pos >= 0 && (null === this.FullRecalc.Id || this.FullRecalc.StartIndex > Pos)))
		return;

	var oSelectedInfo = this.GetSelectedElementsInfo();

	var Math = oSelectedInfo.Get_Math();
	if (null !== Math)
		this.DrawingDocument.Update_MathTrack(true, (false === bSelection || true === bEmptySelection ? true : false), Math);
	else
		this.DrawingDocument.Update_MathTrack(false);

	var oBlockLevelSdt  = oSelectedInfo.GetBlockLevelSdt();
	var oInlineLevelSdt = oSelectedInfo.GetInlineLevelSdt();

	if (oInlineLevelSdt)
		oInlineLevelSdt.DrawContentControlsTrack(false);
	else if (oBlockLevelSdt)
		oBlockLevelSdt.DrawContentControlsTrack(false);
	else
		this.DrawingDocument.OnDrawContentControl(null, c_oContentControlTrack.In);

	var oField = oSelectedInfo.Get_Field();
	if (null !== oField && (fieldtype_MERGEFIELD !== oField.Get_FieldType() || true !== this.MailMergeFieldsHighlight))
	{
		var aBounds = oField.Get_Bounds();
		this.DrawingDocument.Update_FieldTrack(true, aBounds);
	}
	else
	{
		this.DrawingDocument.Update_FieldTrack(false);
	}
};
CDocument.prototype.Document_UpdateUndoRedoState = function()
{
	if (true === this.TurnOffInterfaceEvents)
		return;

	if (true === AscCommon.CollaborativeEditing.Get_GlobalLockSelection())
		return;

	// TODO: Возможно стоит перенсти эту проверку в класс CHistory и присылать
	//       данные события при изменении значения History.Index

	// Проверяем состояние Undo/Redo

	if (this.IsViewModeInReview())
	{
		this.Api.sync_CanUndoCallback(false);
		this.Api.sync_CanRedoCallback(false);
	}
	else
	{
		var bCanUndo = this.History.Can_Undo();
		if (true !== bCanUndo && this.Api && this.CollaborativeEditing && true === this.CollaborativeEditing.Is_Fast() && true !== this.CollaborativeEditing.Is_SingleUser())
			bCanUndo = this.CollaborativeEditing.CanUndo();

		this.Api.sync_CanUndoCallback(bCanUndo);
		this.Api.sync_CanRedoCallback(this.History.Can_Redo());
		this.Api.CheckChangedDocument();
	}
};
CDocument.prototype.Document_UpdateCopyCutState = function()
{
	if (true === this.TurnOffInterfaceEvents)
		return;

	if (true === AscCommon.CollaborativeEditing.Get_GlobalLockSelection())
		return;

	// Во время работы селекта не обновляем состояние
	if (true === this.Selection.Start)
		return;

	this.Api.sync_CanCopyCutCallback(this.Can_CopyCut());
};
CDocument.prototype.Document_UpdateCanAddHyperlinkState = function()
{
	if (true === this.TurnOffInterfaceEvents)
		return;

	if (true === AscCommon.CollaborativeEditing.Get_GlobalLockSelection())
		return;

	// Проверяем можно ли добавить гиперссылку
	this.Api.sync_CanAddHyperlinkCallback(this.CanAddHyperlink(false));
};
CDocument.prototype.Document_UpdateSectionPr = function()
{
	if (true === this.TurnOffInterfaceEvents)
		return;

	if (true === this.CollaborativeEditing.Get_GlobalLockSelection())
		return;

	// Обновляем ориентацию страницы
	this.Api.sync_PageOrientCallback(this.Get_DocumentOrientation());

	// Обновляем размер страницы
	var PageSize = this.Get_DocumentPageSize();
	this.Api.sync_DocSizeCallback(PageSize.W, PageSize.H);

	// Обновляем настройки колонок
	var CurPos = this.CurPos.ContentPos;
	var SectPr = this.SectionsInfo.Get_SectPr(CurPos).SectPr;

	if (SectPr)
	{
		var ColumnsPr = new CDocumentColumnsProps();
		ColumnsPr.From_SectPr(SectPr);
		this.Api.sync_ColumnsPropsCallback(ColumnsPr);
		this.Api.sync_SectionPropsCallback(new CDocumentSectionProps(SectPr));
	}
};
CDocument.prototype.Get_ColumnsProps = function()
{
	// Обновляем настройки колонок
	var CurPos = this.CurPos.ContentPos;
	var SectPr = this.SectionsInfo.Get_SectPr(CurPos).SectPr;

	var ColumnsPr = new CDocumentColumnsProps();
	if (SectPr)
	{
		ColumnsPr.From_SectPr(SectPr);
	}

	return ColumnsPr;
};
/**
 * Отключаем отсылку сообщений в интерфейс.
 */
CDocument.prototype.TurnOff_InterfaceEvents = function()
{
	this.TurnOffInterfaceEvents = true;
};
/**
 * Включаем отсылку сообщений в интерфейс.
 *
 * @param {bool} bUpdate Обновлять ли интерфейс
 */
CDocument.prototype.TurnOn_InterfaceEvents = function(bUpdate)
{
	this.TurnOffInterfaceEvents = false;

	if (true === bUpdate)
	{
		this.Document_UpdateInterfaceState();
		this.Document_UpdateSelectionState();
		this.Document_UpdateRulersState();
	}
};
CDocument.prototype.TurnOff_RecalculateCurPos = function()
{
	this.TurnOffRecalcCurPos = true;
};
CDocument.prototype.TurnOn_RecalculateCurPos = function(bUpdate)
{
	this.TurnOffRecalcCurPos = false;

	if (true === bUpdate)
		this.Document_UpdateSelectionState();
};
CDocument.prototype.Can_CopyCut = function()
{
	var bCanCopyCut = false;

	var LogicDocument  = null;
	var DrawingObjects = null;

	var nDocPosType = this.Get_DocPosType();
	if (docpostype_HdrFtr === nDocPosType)
	{
		var CurHdrFtr = this.HdrFtr.CurHdrFtr;
		if (null !== CurHdrFtr)
		{
			if (docpostype_DrawingObjects === CurHdrFtr.Content.Get_DocPosType())
				DrawingObjects = this.DrawingObjects;
			else
				LogicDocument = CurHdrFtr.Content;
		}
	}
	else if (docpostype_DrawingObjects === nDocPosType)
	{
		DrawingObjects = this.DrawingObjects;
	}
	else if (docpostype_Footnotes === nDocPosType)
	{
		if (0 === this.Footnotes.Selection.Direction)
		{
			var oFootnote = this.Footnotes.GetCurFootnote();
			if (oFootnote)
			{
				if (docpostype_DrawingObjects === oFootnote.Get_DocPosType())
				{
					DrawingObjects = this.DrawingObjects;
				}
				else
				{
					LogicDocument = oFootnote;
				}
			}
		}
		else
		{
			return true;
		}
	}
	else //if (docpostype_Content === nDocPosType)
	{
		LogicDocument = this;
	}

	if (null !== DrawingObjects)
	{
		if (true === DrawingObjects.isSelectedText())
			LogicDocument = DrawingObjects.getTargetDocContent();
		else
			bCanCopyCut = true;
	}

	if (null !== LogicDocument)
	{
		if (true === LogicDocument.IsSelectionUse() && true !== LogicDocument.IsSelectionEmpty(true))
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
//----------------------------------------------------------------------------------------------------------------------
// Функции для работы с номерами страниц
//----------------------------------------------------------------------------------------------------------------------
CDocument.prototype.Get_StartPage_Absolute = function()
{
	return 0;
};
CDocument.prototype.Get_StartPage_Relative = function()
{
	return 0;
};
CDocument.prototype.Get_AbsolutePage = function(CurPage)
{
	return CurPage;
};
CDocument.prototype.Set_CurPage = function(PageNum)
{
	this.CurPage = Math.min(this.Pages.length - 1, Math.max(0, PageNum));
};
CDocument.prototype.Get_CurPage = function()
{
	// Работаем с колонтитулом
	if (docpostype_HdrFtr === this.Get_DocPosType())
		return this.HdrFtr.Get_CurPage();

	return this.CurPage;
};
//----------------------------------------------------------------------------------------------------------------------
// Undo/Redo функции
//----------------------------------------------------------------------------------------------------------------------
CDocument.prototype.Create_NewHistoryPoint = function(Description)
{
	this.History.Create_NewPoint(Description);
};
CDocument.prototype.Document_Undo = function(Options)
{
	if (true === AscCommon.CollaborativeEditing.Get_GlobalLock() && true !== this.IsFillingFormMode())
		return;

	if (true !== this.History.Can_Undo() && this.Api && this.CollaborativeEditing && true === this.CollaborativeEditing.Is_Fast() && true !== this.CollaborativeEditing.Is_SingleUser())
	{
		if (this.CollaborativeEditing.CanUndo() && true === this.Api.canSave)
		{
			this.CollaborativeEditing.Set_GlobalLock(true);
			this.Api.asc_Save(true, true);
		}
	}
	else
	{
		this.DrawingDocument.EndTrackTable(null, true);
		this.DrawingObjects.TurnOffCheckChartSelection();

		this.History.Undo(Options);
		this.DrawingObjects.TurnOnCheckChartSelection();
		this.Recalculate(false, false, this.History.RecalculateData);

		this.Document_UpdateSelectionState();
		this.Document_UpdateInterfaceState();
		this.Document_UpdateRulersState();
	}
};
CDocument.prototype.Document_Redo = function()
{
	if (true === AscCommon.CollaborativeEditing.Get_GlobalLock() && true !== this.IsFillingFormMode())
		return;

	this.DrawingDocument.EndTrackTable(null, true);
	this.DrawingObjects.TurnOffCheckChartSelection();

	this.History.Redo();
	this.DrawingObjects.TurnOnCheckChartSelection();
	this.Recalculate(false, false, this.History.RecalculateData);

	this.Document_UpdateSelectionState();
	this.Document_UpdateInterfaceState();
	this.Document_UpdateRulersState();
};
CDocument.prototype.GetSelectionState = function()
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

	DocState.CurPage    = this.CurPage;
	DocState.CurComment = this.Comments.Get_CurrentId();

	var State = null;
	if (true === editor.isStartAddShape && docpostype_DrawingObjects === this.Get_DocPosType())
	{
		DocState.CurPos.Type     = docpostype_Content;
		DocState.Selection.Start = false;
		DocState.Selection.Use   = false;

		this.Content[DocState.CurPos.ContentPos].RemoveSelection();
		State = this.Content[this.CurPos.ContentPos].GetSelectionState();
	}
	else
	{
		State = this.Controller.GetSelectionState();
	}

	if (null != this.Selection.Data && true === this.Selection.Data.TableBorder)
	{
		DocState.Selection.Data = null;
	}

	State.push(DocState);

	return State;
};
CDocument.prototype.SetSelectionState = function(State)
{
	if (docpostype_DrawingObjects === this.Get_DocPosType())
		this.DrawingObjects.resetSelection();

	if (State.length <= 0)
		return;

	var DocState = State[State.length - 1];

	this.CurPos.X          = DocState.CurPos.X;
	this.CurPos.Y          = DocState.CurPos.Y;
	this.CurPos.ContentPos = DocState.CurPos.ContentPos;
	this.CurPos.RealX      = DocState.CurPos.RealX;
	this.CurPos.RealY      = DocState.CurPos.RealY;
	this.Set_DocPosType(DocState.CurPos.Type);

	this.Selection.Start    = DocState.Selection.Start;
	this.Selection.Use      = DocState.Selection.Use;
	this.Selection.StartPos = DocState.Selection.StartPos;
	this.Selection.EndPos   = DocState.Selection.EndPos;
	this.Selection.Flag     = DocState.Selection.Flag;
	this.Selection.Data     = DocState.Selection.Data;

	this.Selection.DragDrop.Flag = 0;
	this.Selection.DragDrop.Data = null;

	this.CurPage = DocState.CurPage;
	this.Comments.Set_Current(DocState.CurComment);

	this.Controller.SetSelectionState(State, State.length - 2);
};
CDocument.prototype.Get_ParentObject_or_DocumentPos = function(Index)
{
	return {Type : AscDFH.historyitem_recalctype_Inline, Data : Index};
};
CDocument.prototype.Refresh_RecalcData = function(Data)
{
	var ChangePos         = -1;
	var bNeedRecalcHdrFtr = false;

	var Type = Data.Type;

	switch (Type)
	{
		case AscDFH.historyitem_Document_AddItem:
		case AscDFH.historyitem_Document_RemoveItem:
		{
			ChangePos = Data.Pos;
			break;
		}

		case AscDFH.historyitem_Document_DefaultTab:
		case AscDFH.historyitem_Document_EvenAndOddHeaders:
		case AscDFH.historyitem_Document_MathSettings:
		{
			ChangePos = 0;
			break;
		}
	}

	if (-1 != ChangePos)
	{
		this.History.RecalcData_Add({
			Type : AscDFH.historyitem_recalctype_Inline,
			Data : {Pos : ChangePos, PageNum : 0}
		});
	}
};
CDocument.prototype.Refresh_RecalcData2 = function(Index, Page_rel)
{
	this.History.RecalcData_Add({
		Type : AscDFH.historyitem_recalctype_Inline,
		Data : {Pos : Index, PageNum : Page_rel}
	});
};
//----------------------------------------------------------------------------------------------------------------------
// Функции для работы с гиперссылками
//----------------------------------------------------------------------------------------------------------------------
CDocument.prototype.AddHyperlink = function(HyperProps)
{
	// Проверку, возможно ли добавить гиперссылку, должны были вызвать до этой функции
	if (null != HyperProps.Text && "" != HyperProps.Text && true === this.IsSelectionUse())
	{
		// Корректировка в данном случае пройдет при добавлении гиперссылки.
		var SelectionInfo = this.GetSelectedElementsInfo();
		var Para          = SelectionInfo.GetParagraph();
		if (null !== Para)
			HyperProps.TextPr = Para.Get_TextPr(Para.Get_ParaContentPos(true, true));

		this.Remove(1, false, false, true);
		this.RemoveTextSelection();
	}

	this.Controller.AddHyperlink(HyperProps);
	this.Recalculate();
	this.Document_UpdateInterfaceState();
	this.Document_UpdateSelectionState();
};
CDocument.prototype.ModifyHyperlink = function(HyperProps)
{
	this.Controller.ModifyHyperlink(HyperProps);
	this.Recalculate();
    this.Document_UpdateSelectionState();
    this.Document_UpdateInterfaceState();
};
CDocument.prototype.RemoveHyperlink = function()
{
	this.Controller.RemoveHyperlink();
	this.Recalculate();
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.CanAddHyperlink = function(bCheckInHyperlink)
{
	return this.Controller.CanAddHyperlink(bCheckInHyperlink);
};
/**
 * Проверяем, находимся ли мы в гиперссылке сейчас.
 * @param bCheckEnd
 * @returns {*}
 */
CDocument.prototype.IsCursorInHyperlink = function(bCheckEnd)
{
	if (undefined === bCheckEnd)
		bCheckEnd = true;

	return this.Controller.IsCursorInHyperlink(bCheckEnd);
};
//----------------------------------------------------------------------------------------------------------------------
// Функции для работы с совместным редактирования
//----------------------------------------------------------------------------------------------------------------------
CDocument.prototype.Document_Is_SelectionLocked = function(CheckType, AdditionalData, DontLockInFastMode, isIgnoreCanEditFlag)
{
	return false;
};
CDocument.prototype.Get_SelectionState2 = function()
{
	this.RemoveSelection();

	// Сохраняем Id ближайшего элемента в текущем классе
	var State       = new CDocumentSelectionState();
	var nDocPosType = this.Get_DocPosType();
	if (docpostype_HdrFtr === nDocPosType)
	{
		State.Type = docpostype_HdrFtr;

		if (null != this.HdrFtr.CurHdrFtr)
			State.Id = this.HdrFtr.CurHdrFtr.Get_Id();
		else
			State.Id = null;
	}
	else if (docpostype_DrawingObjects === nDocPosType)
	{
		// TODO: запрашиваем параграф текущего выделенного элемента
		var X       = 0;
		var Y       = 0;
		var PageNum = this.CurPage;

		var ContentPos = this.Internal_GetContentPosByXY(X, Y, PageNum);

		State.Type = docpostype_Content;
		State.Id   = this.Content[ContentPos].GetId();
	}
	else if (docpostype_Footnotes === nDocPosType)
	{
		State.Type = docpostype_Footnotes;
		State.Id   = this.Footnotes.GetCurFootnote().Get_Id();
	}
	else // if (docpostype_Content === nDocPosType)
	{
		State.Id   = this.Get_Id();
		State.Type = docpostype_Content;

		var Element = this.Content[this.CurPos.ContentPos];
		State.Data  = Element.Get_SelectionState2();
	}

	return State;
};
CDocument.prototype.Set_SelectionState2 = function(State)
{
	this.RemoveSelection();

	var Id = State.Id;
	if (docpostype_HdrFtr === State.Type)
	{
		this.Set_DocPosType(docpostype_HdrFtr);

		if (null === Id || true != this.HdrFtr.Set_CurHdrFtr_ById(Id))
		{
			this.Set_DocPosType(docpostype_Content);
			this.CurPos.ContentPos = 0;

			this.Content[this.CurPos.ContentPos].MoveCursorToStartPos(false);
		}
	}
	else if (docpostype_Footnotes === State.Type)
	{
		this.Set_DocPosType(docpostype_Footnotes);
		var oFootnote = g_oTableId.Get_ById(State.Id);
		if (oFootnote && true === this.Footnotes.Is_UseInDocument(State.Id))
		{
			this.Footnotes.private_SetCurrentFootnoteNoSelection(oFootnote);
			oFootnote.MoveCursorToStartPos(false);
		}
		else
		{
			this.EndFootnotesEditing();
		}
	}
	else // if ( docpostype_Content === State.Type )
	{
		var CurId = State.Data.Id;

		var bFlag = false;

		var Pos = 0;

		// Найдем элемент с Id = CurId
		var Count = this.Content.length;
		for (Pos = 0; Pos < Count; Pos++)
		{
			if (this.Content[Pos].GetId() == CurId)
			{
				bFlag = true;
				break;
			}
		}

		if (true !== bFlag)
		{
			var TempElement = g_oTableId.Get_ById(CurId);
			Pos             = ( null != TempElement ? TempElement.Index : 0 );
			Pos             = Math.max(0, Math.min(Pos, this.Content.length - 1));
		}

		this.Selection.Start    = false;
		this.Selection.Use      = false;
		this.Selection.StartPos = Pos;
		this.Selection.EndPos   = Pos;
		this.Selection.Flag     = selectionflag_Common;

		this.Set_DocPosType(docpostype_Content);
		this.CurPos.ContentPos = Pos;

		if (true !== bFlag)
			this.Content[this.CurPos.ContentPos].MoveCursorToStartPos(false);
		else
			this.Content[this.CurPos.ContentPos].SetSelectionState2(State.Data);
	}
};
//----------------------------------------------------------------------------------------------------------------------
// Функции для работы с комментариями
//----------------------------------------------------------------------------------------------------------------------
CDocument.prototype.AddComment = function(CommentData)
{
	if (true != this.CanAddComment())
	{
		CommentData.Set_QuoteText(null);
		var Comment = new CComment(this.Comments, CommentData);
		this.Comments.Add(Comment);

		// Обновляем информацию для Undo/Redo
		this.Document_UpdateInterfaceState();
	}
	else
	{
		var QuotedText = this.GetSelectedText(false);
		if (null === QuotedText)
			QuotedText = "";
		CommentData.Set_QuoteText(QuotedText);

		var Comment = new CComment(this.Comments, CommentData);
		this.Comments.Add(Comment);
		this.Controller.AddComment(Comment);

		// TODO: Продумать, как избавиться от пересчета
		this.Recalculate();
		this.Document_UpdateInterfaceState();
	}

	return Comment;
};
CDocument.prototype.EditComment = function(Id, CommentData)
{
	if (!this.Comments.IsUseSolved() && this.Comments.Get_CurrentId() === Id)
	{
		var oComment = this.Comments.Get_ById(Id);
		if (oComment && !oComment.IsSolved() && CommentData.IsSolved())
		{
			this.Comments.Set_Current(null);
			this.Api.sync_HideComment();
			this.DrawingDocument.ClearCachePages();
			this.DrawingDocument.FirePaint();
		}
	}

	this.Comments.Set_CommentData(Id, CommentData);
	this.Document_UpdateInterfaceState();
};
CDocument.prototype.RemoveComment = function(Id, bSendEvent, bRecalculate)
{
	if (null === Id)
		return;

	if (true === this.Comments.Remove_ById(Id))
	{
		if (true === bRecalculate)
		{
			// TODO: Продумать как избавиться от пересчета при удалении комментария
			this.Recalculate();
			this.Document_UpdateInterfaceState();
		}

		if (true === bSendEvent)
			this.Api.sync_RemoveComment(Id);
	}
};
CDocument.prototype.CanAddComment = function()
{
	if (!this.CanEdit() && !this.IsEditCommentsMode())
		return false;

	if (true !== this.Comments.Is_Use())
		return false;

	return this.Controller.CanAddComment();
};
CDocument.prototype.SelectComment = function(Id, ScrollToComment)
{
	var OldId = this.Comments.Get_CurrentId();
	this.Comments.Set_Current(Id);

	var Comment = this.Comments.Get_ById(Id);
	if (null != Comment)
	{
		var Comment_PageNum = Comment.m_oStartInfo.PageNum;
		var Comment_Y       = Comment.m_oStartInfo.Y;
		var Comment_X       = Comment.m_oStartInfo.X;

		if (true === ScrollToComment)
			this.DrawingDocument.m_oWordControl.ScrollToPosition(Comment_X, Comment_Y, Comment_PageNum);
	}

	if (OldId != Id)
	{
		this.DrawingDocument.ClearCachePages();
		this.DrawingDocument.FirePaint();
	}
};
CDocument.prototype.ShowComment = function(Id)
{
	var Comment = this.Comments.Get_ById(Id);
	if (null != Comment && null != Comment.StartId && null != Comment.EndId)
	{
		var Comment_PageNum = Comment.m_oStartInfo.PageNum;
		var Comment_Y       = Comment.m_oStartInfo.Y;
		var Comment_X       = this.Get_PageLimits(Comment_PageNum).XLimit;

		var Coords = this.DrawingDocument.ConvertCoordsToCursorWR(Comment_X, Comment_Y, Comment_PageNum);
		this.Api.sync_ShowComment(Comment.Get_Id(), Coords.X, Coords.Y);
	}
	else
	{
		this.Api.sync_HideComment();
	}
};
CDocument.prototype.ShowComments = function(isShowSolved)
{
	if (false !== isShowSolved)
		isShowSolved = true;

	this.Comments.Set_Use(true);
	this.Comments.SetUseSolved(isShowSolved);
	this.DrawingDocument.ClearCachePages();
	this.DrawingDocument.FirePaint();
};
CDocument.prototype.HideComments = function()
{
	this.Comments.Set_Use(false);
	this.Comments.SetUseSolved(false);
	this.Comments.Set_Current(null);
	this.DrawingDocument.ClearCachePages();
	this.DrawingDocument.FirePaint();
};
CDocument.prototype.GetPrevElementEndInfo = function(CurElement)
{
    var PrevElement = CurElement.Get_DocumentPrev();

    if (null !== PrevElement && undefined !== PrevElement)
        return PrevElement.GetEndInfo();
    else
        return null;
};
CDocument.prototype.GetSelectionAnchorPos = function()
{
	var Result = this.Controller.GetSelectionAnchorPos();

	var PageLimit = this.Get_PageLimits(Result.Page);
	Result.X0     = PageLimit.X;
	Result.X1     = PageLimit.XLimit;

	var Coords0 = this.DrawingDocument.ConvertCoordsToCursorWR(Result.X0, Result.Y, Result.Page);
	var Coords1 = this.DrawingDocument.ConvertCoordsToCursorWR(Result.X1, Result.Y, Result.Page);

	return {X0 : Coords0.X, X1 : Coords1.X, Y : Coords0.Y};
};
//----------------------------------------------------------------------------------------------------------------------
// Функции для работы с textbox
//----------------------------------------------------------------------------------------------------------------------
CDocument.prototype.TextBox_Put = function(sText, rFonts)
{
	if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
	{
		this.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddTextFromTextBox);

		// Отключаем пересчет, включим перед последним добавлением. Поскольку,
		// у нас все добавляется в 1 параграф, так можно делать.
		this.Start_SilentMode();

		if (undefined === rFonts)
		{
			var Count = sText.length;
			var e     = AscCommon.global_keyboardEvent;
			for (var Index = 0; Index < Count; Index++)
			{
				var _char = sText.charAt(Index);
				if (" " == _char)
					this.AddToParagraph(new ParaSpace());
				else
					this.AddToParagraph(new ParaText(_char));
			}
		}
		else
		{
			var Para = this.GetCurrentParagraph();
			if (null === Para)
				return;

			var RunPr = Para.Get_TextPr();
			if (null === RunPr || undefined === RunPr)
				RunPr = new CTextPr();

			RunPr.RFonts = rFonts;

			var Run = new ParaRun(Para);
			Run.Set_Pr(RunPr);

			var Count = sText.length;
			for (var Index = 0; Index < Count; Index++)
			{
				var _char = sText.charAt(Index);
				if (" " == _char)
					Run.Add_ToContent(Index, new ParaSpace(), false);
				else
					Run.Add_ToContent(Index, new ParaText(_char), false);
			}

			Para.Add(Run);
		}

		this.End_SilentMode(true);
	}
};
//----------------------------------------------------------------------------------------------------------------------
// события вьюера
//----------------------------------------------------------------------------------------------------------------------
CDocument.prototype.Viewer_OnChangePosition = function()
{
	var Comment = this.Comments.Get_Current();
	if (null != Comment)
	{
		var Comment_PageNum = Comment.m_oStartInfo.PageNum;
		var Comment_Y       = Comment.m_oStartInfo.Y;
		var Comment_X       = this.Get_PageLimits(Comment_PageNum).XLimit;
		var Para            = g_oTableId.Get_ById(Comment.StartId);

		if (null !== Para)
		{
			var TextTransform = Para.Get_ParentTextTransform();
			if (TextTransform)
			{
				Comment_Y = TextTransform.TransformPointY(Comment.m_oStartInfo.X, Comment.m_oStartInfo.Y);
			}
		}

		var Coords = this.DrawingDocument.ConvertCoordsToCursorWR(Comment_X, Comment_Y, Comment_PageNum);
		this.Api.sync_UpdateCommentPosition(Comment.Get_Id(), Coords.X, Coords.Y);
	}
    window['AscCommon'].g_clipboardBase.SpecialPasteButton_Update_Position();
	this.TrackRevisionsManager.Update_VisibleChangesPosition(this.Api);
};
//----------------------------------------------------------------------------------------------------------------------
// Функции для работы с секциями
//----------------------------------------------------------------------------------------------------------------------
CDocument.prototype.Update_SectionsInfo = function()
{
	this.SectionsInfo.Clear();

	var Count = this.Content.length;
	for (var Index = 0; Index < Count; Index++)
	{
		var Element = this.Content[Index];
		if (type_Paragraph === Element.GetType() && undefined !== Element.Get_SectionPr())
			this.SectionsInfo.Add(Element.Get_SectionPr(), Index);
	}

	this.SectionsInfo.Add(this.SectPr, Count);

	// Когда полностью обновляются секции надо пересчитывать с самого начала
	this.RecalcInfo.Set_NeedRecalculateFromStart(true);
};
CDocument.prototype.Check_SectionLastParagraph = function()
{
	var Count = this.Content.length;
	if (Count <= 0)
		return;

	var Element = this.Content[Count - 1];
	if (type_Paragraph === Element.GetType() && undefined !== Element.Get_SectionPr())
		this.Internal_Content_Add(Count, new Paragraph(this.DrawingDocument, this));
};
CDocument.prototype.Add_SectionBreak = function(SectionBreakType)
{
	if (docpostype_Content !== this.Get_DocPosType())
		return false;

	if (true === this.Selection.Use)
	{
		// Если у нас есть селект, тогда ставим курсор в начало селекта
		this.MoveCursorLeft(false, false);
	}

	var Element = this.Content[this.CurPos.ContentPos];

	var CurSectPr = this.SectionsInfo.Get_SectPr(this.CurPos.ContentPos).SectPr;

	if (type_Paragraph === Element.GetType())
	{
		// Если мы стоим в параграфе, тогда делим данный параграф на 2 в текущей точке(даже если мы стоим в начале
		// или в конце параграфа) и к первому параграфу приписываем конец секкции.

		var NewParagraph = new Paragraph(this.DrawingDocument, this);

		Element.Split(NewParagraph);

		this.CurPos.ContentPos++;
		NewParagraph.MoveCursorToStartPos(false);

		this.Internal_Content_Add(this.CurPos.ContentPos, NewParagraph);

		// Заметим, что после функции Split, у параграфа Element не может быть окончания секции, т.к. если она
		// была в нем изначально, тогда после функции Split, окончание секции перенеслось в новый параграф.
	}
	else if (type_Table === Element.GetType())
	{
		// Если мы стоим в таблице, тогда делим данную таблицу на 2 по текущему ряду(текущий ряд попадает во
		// вторую таблицу). Вставляем между таблицами параграф, и к этому параграфу приписываем окончание
		// секции. Если мы стоим в первой строке таблицы, таблицу делить не надо, достаточно добавить новый
		// параграф перед ней.

		var NewParagraph = new Paragraph(this.DrawingDocument, this);
		var NewTable     = Element.Split_Table();

		if (null === NewTable)
		{
			this.Internal_Content_Add(this.CurPos.ContentPos, NewParagraph);
			this.CurPos.ContentPos++;
		}
		else
		{
			this.Internal_Content_Add(this.CurPos.ContentPos + 1, NewParagraph);
			this.Internal_Content_Add(this.CurPos.ContentPos + 2, NewTable);
			this.CurPos.ContentPos += 2;
		}

		this.Content[this.CurPos.ContentPos].MoveCursorToStartPos(false);

		Element = NewParagraph;
	}
	else
	{
		return false;
	}

	var SectPr = new CSectionPr(this);

	// В данном месте мы ставим разрыв секции. Чтобы до текущего места ничего не изменилось, мы у новой
	// для новой секции копируем все настройки из старой, а в старую секцию выставляем приходящий тип
	// разрыва секций. Заметим, что поскольку мы делаем все так, чтобы до текущей страницы ничего не
	// изменилось, надо сохранить эту информацию для пересчета, для этого мы помечаем все следующие изменения
	// как не влияющие на пересчет.

	this.History.MinorChanges = true;

	SectPr.Copy(CurSectPr);
	CurSectPr.Set_Type(SectionBreakType);
	CurSectPr.Set_PageNum_Start(-1);
	CurSectPr.Clear_AllHdrFtr();

	this.History.MinorChanges = false;

	Element.Set_SectionPr(SectPr);
	Element.Refresh_RecalcData2(0, 0);

	this.Recalculate();
	this.Document_UpdateInterfaceState();
	this.Document_UpdateSelectionState();

	return true;
};
CDocument.prototype.Get_SectionFirstPage = function(SectIndex, Page_abs)
{
	if (SectIndex <= 0)
		return 0;

	var StartIndex = this.SectionsInfo.Get_SectPr2(SectIndex - 1).Index;

	// Ищем номер страницы, на которой закончилась предыдущая секция
	var CurPage = Page_abs;
	for (; CurPage > 0; CurPage--)
	{
		if (this.Pages[CurPage].EndPos >= StartIndex && this.Pages[CurPage].Pos <= StartIndex)
			break;
	}

	return CurPage + 1;
};
CDocument.prototype.Get_SectionPageNumInfo = function(Page_abs)
{
	var PageNumInfo = this.Get_SectionPageNumInfo2(Page_abs);

	var FP = PageNumInfo.FirstPage;
	var CP = PageNumInfo.CurPage;

	// Первая страница учитывается, только если параграф, идущий сразу за разрывом секции, начинается с новой страницы
	var bCheckFP  = true;
	var SectIndex = PageNumInfo.SectIndex;
	if (SectIndex > 0)
	{
		var CurSectInfo  = this.SectionsInfo.Get_SectPr2(SectIndex);
		var PrevSectInfo = this.SectionsInfo.Get_SectPr2(SectIndex - 1);

		if (CurSectInfo !== PrevSectInfo && c_oAscSectionBreakType.Continuous === CurSectInfo.SectPr.Get_Type() && true === CurSectInfo.SectPr.Compare_PageSize(PrevSectInfo.SectPr))
		{
			var ElementIndex = PrevSectInfo.Index;
			if (ElementIndex < this.Content.length - 1 && true !== this.Content[ElementIndex + 1].IsStartFromNewPage())
				bCheckFP = false;
		}
	}


	var bFirst = ( FP === CP && true === bCheckFP ? true : false );
	var bEven  = ( 0 === CP % 2 ? true : false ); // Четность/нечетность проверяется по текущему номеру страницы в секции, с учетом нумерации в секциях

	return new CSectionPageNumInfo(FP, CP, bFirst, bEven, Page_abs);
};
CDocument.prototype.Get_SectionPageNumInfo2 = function(Page_abs)
{
	var StartIndex = 0;

	// Такое может случится при первом рассчете документа, и когда мы находимся в автофигуре
	if (undefined !== this.Pages[Page_abs])
		StartIndex = this.Pages[Page_abs].Pos;

	var SectIndex      = this.SectionsInfo.Get_Index(StartIndex);
	var StartSectIndex = SectIndex;

	if (0 === SectIndex)
	{
		var PageNumStart = this.SectionsInfo.Get_SectPr2(0).SectPr.Get_PageNum_Start();
		var BT           = this.SectionsInfo.Get_SectPr2(0).SectPr.Get_Type();

		// Нумерация начинается с 1, если начальное значение не задано. Заметим, что в Word нумерация может начинаться и
		// со значения 0, а все отрицательные значения воспринимаются как продолжение нумерации с предыдущей секции.
		if (PageNumStart < 0)
			PageNumStart = 1;

		if ((c_oAscSectionBreakType.OddPage === BT && 0 === PageNumStart % 2) || (c_oAscSectionBreakType.EvenPage === BT && 1 === PageNumStart % 2))
			PageNumStart++;

		return {FirstPage : PageNumStart, CurPage : Page_abs + PageNumStart, SectIndex : StartSectIndex};
	}

	var SectionFirstPage = this.Get_SectionFirstPage(SectIndex, Page_abs);

	var FirstPage    = SectionFirstPage;
	var PageNumStart = this.SectionsInfo.Get_SectPr2(SectIndex).SectPr.Get_PageNum_Start();
	var BreakType    = this.SectionsInfo.Get_SectPr2(SectIndex).SectPr.Get_Type();

	var StartInfo = [];
	StartInfo.push({FirstPage : FirstPage, BreakType : BreakType});

	while (PageNumStart < 0 && SectIndex > 0)
	{
		SectIndex--;

		FirstPage    = this.Get_SectionFirstPage(SectIndex, Page_abs);
		PageNumStart = this.SectionsInfo.Get_SectPr2(SectIndex).SectPr.Get_PageNum_Start();
		BreakType    = this.SectionsInfo.Get_SectPr2(SectIndex).SectPr.Get_Type();

		StartInfo.splice(0, 0, {FirstPage : FirstPage, BreakType : BreakType});
	}

	// Нумерация начинается с 1, если начальное значение не задано. Заметим, что в Word нумерация может начинаться и
	// со значения 0, а все отрицательные значения воспринимаются как продолжение нумерации с предыдущей секции.
	if (PageNumStart < 0)
		PageNumStart = 1;

	var InfoIndex = 0;
	var InfoCount = StartInfo.length;

	var FP     = StartInfo[0].FirstPage;
	var BT     = StartInfo[0].BreakType;
	var PrevFP = StartInfo[0].FirstPage;

	while (InfoIndex < InfoCount)
	{
		FP = StartInfo[InfoIndex].FirstPage;
		BT = StartInfo[InfoIndex].BreakType;

		PageNumStart += FP - PrevFP;
		PrevFP = FP;

		if ((c_oAscSectionBreakType.OddPage === BT && 0 === PageNumStart % 2) || (c_oAscSectionBreakType.EvenPage === BT && 1 === PageNumStart % 2))
			PageNumStart++;

		InfoIndex++;
	}

	if (FP > Page_abs)
		Page_abs = FP;

	var _FP = PageNumStart;
	var _CP = PageNumStart + Page_abs - FP;

	return {FirstPage : _FP, CurPage : _CP, SectIndex : StartSectIndex};
};
CDocument.prototype.Get_SectionHdrFtr = function(Page_abs, _bFirst, _bEven)
{
	var StartIndex = this.Pages[Page_abs].Pos;
	var SectIndex  = this.SectionsInfo.Get_Index(StartIndex);
	var CurSectPr  = this.SectionsInfo.Get_SectPr2(SectIndex).SectPr;

	var bEven  = ( true === _bEven && true === EvenAndOddHeaders ? true : false );
	var bFirst = ( true === _bFirst && true === CurSectPr.TitlePage ? true : false );

	var CurSectIndex = SectIndex;

	// Ищем верхний и нижний колонтитулы. Если они не находятся в текущей секции, тогда ищем в предыдущей.
	var Header = null, Footer = null;
	while (CurSectIndex >= 0)
	{
		var SectPr = this.SectionsInfo.Get_SectPr2(CurSectIndex).SectPr;

		if (null === Header)
		{
			if (true === bFirst)
				Header = SectPr.Get_Header_First();
			else if (true === bEven)
				Header = SectPr.Get_Header_Even();
			else
				Header = SectPr.Get_Header_Default();
		}

		if (null === Footer)
		{
			if (true === bFirst)
				Footer = SectPr.Get_Footer_First();
			else if (true === bEven)
				Footer = SectPr.Get_Footer_Even();
			else
				Footer = SectPr.Get_Footer_Default();
		}

		if (null !== Header && null !== Footer)
			break;

		CurSectIndex--;
	}

	return {Header : Header, Footer : Footer, SectPr : CurSectPr};
};
CDocument.prototype.Create_SectionHdrFtr = function(Type, PageIndex)
{
	// Данная функция используется, когда у нас нет колонтитула вообще. Это значит, что его нет ни в 1 секции. Следовательно,
	// создаем колонтитул в первой секции, а в остальных он будет повторяться. По текущей секции нам надо будет
	// определить какой конкретно колонтитул мы собираемся создать.

	var SectionPageInfo = this.Get_SectionPageNumInfo(PageIndex);

	var _bFirst = SectionPageInfo.bFirst;
	var _bEven  = SectionPageInfo.bEven;

	var StartIndex = this.Pages[PageIndex].Pos;
	var SectIndex  = this.SectionsInfo.Get_Index(StartIndex);
	var CurSectPr  = this.SectionsInfo.Get_SectPr2(SectIndex).SectPr;

	var bEven  = ( true === _bEven && true === EvenAndOddHeaders ? true : false );
	var bFirst = ( true === _bFirst && true === CurSectPr.TitlePage ? true : false );

	var SectPr = this.SectionsInfo.Get_SectPr2(0).SectPr;
	var HdrFtr = new CHeaderFooter(this.HdrFtr, this, this.DrawingDocument, Type);

	if (hdrftr_Header === Type)
	{
		if (true === bFirst)
			SectPr.Set_Header_First(HdrFtr);
		else if (true === bEven)
			SectPr.Set_Header_Even(HdrFtr);
		else
			SectPr.Set_Header_Default(HdrFtr);
	}
	else
	{
		if (true === bFirst)
			SectPr.Set_Footer_First(HdrFtr);
		else if (true === bEven)
			SectPr.Set_Footer_Even(HdrFtr);
		else
			SectPr.Set_Footer_Default(HdrFtr);
	}

	return HdrFtr;
};
CDocument.prototype.On_SectionChange = function(_SectPr)
{
	var Index = this.SectionsInfo.Find(_SectPr);
	if (-1 === Index)
		return;

	var SectPr  = null;
	var HeaderF = null, HeaderD = null, HeaderE = null, FooterF = null, FooterD = null, FooterE = null;

	while (Index >= 0)
	{
		SectPr = this.SectionsInfo.Get_SectPr2(Index).SectPr;

		if (null === HeaderF)
			HeaderF = SectPr.Get_Header_First();

		if (null === HeaderD)
			HeaderD = SectPr.Get_Header_Default();

		if (null === HeaderE)
			HeaderE = SectPr.Get_Header_Even();

		if (null === FooterF)
			FooterF = SectPr.Get_Footer_First();

		if (null === FooterD)
			FooterD = SectPr.Get_Footer_Default();

		if (null === FooterE)
			FooterE = SectPr.Get_Footer_Even();

		Index--;
	}

	if (null !== HeaderF)
		HeaderF.Refresh_RecalcData_BySection(_SectPr);

	if (null !== HeaderD)
		HeaderD.Refresh_RecalcData_BySection(_SectPr);

	if (null !== HeaderE)
		HeaderE.Refresh_RecalcData_BySection(_SectPr);

	if (null !== FooterF)
		FooterF.Refresh_RecalcData_BySection(_SectPr);

	if (null !== FooterD)
		FooterD.Refresh_RecalcData_BySection(_SectPr);

	if (null !== FooterE)
		FooterE.Refresh_RecalcData_BySection(_SectPr);
};
CDocument.prototype.Create_HdrFtrWidthPageNum = function(PageIndex, AlignV, AlignH)
{
	// Определим четность страницы и является ли она первой в данной секции. Заметим, что четность страницы
	// отсчитывается от начала текущей секции и не зависит от настроек нумерации страниц для данной секции.
	var SectionPageInfo = this.Get_SectionPageNumInfo(PageIndex);

	var bFirst = SectionPageInfo.bFirst;
	var bEven  = SectionPageInfo.bEven;

	// Запросим нужный нам колонтитул
	var HdrFtr = this.Get_SectionHdrFtr(PageIndex, bFirst, bEven);

	switch (AlignV)
	{
		case hdrftr_Header :
		{
			var Header = HdrFtr.Header;

			if (null === Header)
				Header = this.Create_SectionHdrFtr(hdrftr_Header, PageIndex);

			Header.AddPageNum(AlignH);

			break;
		}

		case hdrftr_Footer :
		{
			var Footer = HdrFtr.Footer;

			if (null === Footer)
				Footer = this.Create_SectionHdrFtr(hdrftr_Footer, PageIndex);

			Footer.AddPageNum(AlignH);

			break;
		}
	}

	this.Recalculate();
};
CDocument.prototype.GetCurrentSectionPr = function()
{
	var oSectPr = this.Controller.GetCurrentSectionPr();
	if (null === oSectPr)
		return this.controller_GetCurrentSectionPr();

	return oSectPr;
};
CDocument.prototype.GetFirstElementInSection = function(SectionIndex)
{
	if (SectionIndex <= 0)
		return this.Content[0] ? this.Content[0] : null;

	var nElementPos = this.SectionsInfo.Get_SectPr2(SectionIndex - 1).Index + 1;
	return this.Content[nElementPos] ? this.Content[nElementPos] : null;
};
CDocument.prototype.GetSectionIndexByElementIndex = function(ElementIndex)
{
	return this.SectionsInfo.Get_Index(ElementIndex);
};

/**
 * Определяем использовать ли заливку текста в особых случаях, когда вызывается заливка параграфа.
 * @param bUse
 */
CDocument.prototype.Set_UseTextShd = function(bUse)
{
	this.UseTextShd = bUse;
};
CDocument.prototype.Recalculate_FromStart = function(bUpdateStates)
{
	var RecalculateData = {
		Inline   : {Pos : 0, PageNum : 0},
		Flow     : [],
		HdrFtr   : [],
		Drawings : {All : true, Map : {}}
	};

	this.Reset_RecalculateCache();
	this.Recalculate(false, false, RecalculateData);

	if (true === bUpdateStates)
	{
		this.Document_UpdateInterfaceState();
		this.Document_UpdateSelectionState();
	}
};
CDocument.prototype.Register_Field = function(oField)
{
	this.FieldsManager.Register_Field(oField);
};
CDocument.prototype.Is_MailMergePreviewResult = function()
{
	return this.MailMergePreview;
};
CDocument.prototype.Is_HightlightMailMergeFields = function()
{
	return this.MailMergeFieldsHighlight;
};
CDocument.prototype.CompareDrawingsLogicPositions = function(Drawing1, Drawing2)
{
	var ParentPara1 = Drawing1.GetParagraph();
	var ParentPara2 = Drawing2.GetParagraph();

	if (!ParentPara1 || !ParentPara2 || !ParentPara1.Parent || !ParentPara2.Parent)
		return 0;

	var TopDocument1 = ParentPara1.Parent.Is_TopDocument(true);
	var TopDocument2 = ParentPara2.Parent.Is_TopDocument(true);

	if (TopDocument1 !== TopDocument2 || !TopDocument1)
		return 0;

	var TopElement1 = ParentPara1.GetTopElement();
	var TopElement2 = ParentPara2.GetTopElement();

	if (!TopElement1 || !TopElement2)
		return 0;

	var TopIndex1 = TopElement1.Get_Index();
	var TopIndex2 = TopElement2.Get_Index();

	if (TopIndex1 < TopIndex2)
		return 1;
	else if (TopIndex1 > TopIndex2)
		return -1;

	if (undefined !== TopDocument1.Content[TopIndex1])
	{
		var CompareEngine = new CDocumentCompareDrawingsLogicPositions(Drawing1, Drawing2);
		TopDocument1.Content[TopIndex1].CompareDrawingsLogicPositions(CompareEngine);
		return CompareEngine.Result;
	}

	return 0;
};
CDocument.prototype.GetTopElement = function()
{
	return null;
};
CDocument.prototype.private_StartSelectionFromCurPos = function()
{
	this.private_UpdateCursorXY(true, true);
	var CurPara = this.GetCurrentParagraph();

	if (null !== CurPara)
	{
		var MouseEvent = new AscCommon.CMouseEventHandler();

		MouseEvent.ClickCount = 1;
		MouseEvent.Type       = AscCommon.g_mouse_event_type_down;

		var X = CurPara.CurPos.RealX;
		var Y = CurPara.CurPos.RealY;

		var DrawMatrix = CurPara.Get_ParentTextTransform();
		if (DrawMatrix)
		{
			var _X = DrawMatrix.TransformPointX(X, Y);
			var _Y = DrawMatrix.TransformPointY(X, Y);

			X = _X;
			Y = _Y;
		}

		this.CurPage = CurPara.Get_CurrentPage_Absolute();
		this.Selection_SetStart(X, Y, MouseEvent);
		MouseEvent.Type = AscCommon.g_mouse_event_type_move;
		this.Selection_SetEnd(X, Y, MouseEvent);
	}
};
CDocument.prototype.private_StopSelection = function()
{
	this.Selection.Start = false;
};
CDocument.prototype.private_UpdateCurPage = function()
{
	if (true === this.TurnOffRecalcCurPos)
		return;

	this.private_CheckCurPage();
};
CDocument.prototype.private_UpdateCursorXY = function(bUpdateX, bUpdateY)
{
	this.private_UpdateCurPage();

	var NewCursorPos = null;

	if (true !== this.IsSelectionUse() || true === this.IsSelectionEmpty())
	{
		NewCursorPos = this.Controller.RecalculateCurPos();
		if (NewCursorPos && NewCursorPos.Transform)
		{
			var x = NewCursorPos.Transform.TransformPointX(NewCursorPos.X, NewCursorPos.Y);
			var y = NewCursorPos.Transform.TransformPointY(NewCursorPos.X, NewCursorPos.Y);

			NewCursorPos.X = x;
			NewCursorPos.Y = y;
		}
	}
	else
	{
		// Обновляем всегда по концу селекта
		var SelectionBounds = this.GetSelectionBounds();
		if (null !== SelectionBounds)
		{
			NewCursorPos = {};
			if (-1 === SelectionBounds.Direction)
			{
				NewCursorPos.X = SelectionBounds.Start.X;
				NewCursorPos.Y = SelectionBounds.Start.Y;

				if (this.CurPage < SelectionBounds.Start.Page)
					NewCursorPos.Y = this.Pages[this.CurPage].Height;
			}
			else
			{
				NewCursorPos.X = SelectionBounds.End.X + SelectionBounds.End.W;
				NewCursorPos.Y = SelectionBounds.End.Y + SelectionBounds.End.H;

				if (this.CurPage > SelectionBounds.End.Page)
					NewCursorPos.Y = 0;
			}
		}
	}

	if (null === NewCursorPos || undefined === NewCursorPos)
		return;

	var RealX = NewCursorPos.X;
	var RealY = NewCursorPos.Y;

	var CurPara = this.GetCurrentParagraph();

	if (bUpdateX)
	{
		this.CurPos.RealX = RealX;

		if (null !== CurPara)
			CurPara.CurPos.RealX = RealX;
	}

	if (bUpdateY)
	{
		this.CurPos.RealY = RealY;

		if (null !== CurPara)
			CurPara.CurPos.RealY = RealY;
	}

	if (true === this.Selection.Use && true !== this.Selection.Start)
		this.private_OnSelectionEnd();
};
CDocument.prototype.private_MoveCursorDown = function(StartX, StartY, AddToSelect)
{
	var StartPage = this.CurPage;
	var CurY      = StartY;

	var PageH = this.Pages[this.CurPage].Height;

	this.TurnOff_InterfaceEvents();
	this.CheckEmptyElementsOnSelection = false;

	var Result = false;
	while (true)
	{
		CurY += 0.1;

		if (CurY > PageH || this.CurPage > StartPage)
		{
			this.CurPage = StartPage;
			if (this.Pages.length - 1 <= this.CurPage)
			{
				Result = false;
				break;
			}
			else
			{
				this.CurPage++;
				StartY = 0;

				var NewPage = this.CurPage;
				var bBreak = false;
				while (true)
				{
					this.MoveCursorToXY(StartX, StartY, AddToSelect);
					this.private_UpdateCursorXY(false, true);

					if (this.CurPage < NewPage)
					{
						StartY += 0.1;
						if (StartY > this.Pages[NewPage].Height)
						{
							NewPage++;
							if (this.Pages.length - 1 < NewPage)
							{
								Result = false;
								break;
							}

							StartY = 0;
						}
						else
						{
							StartY += 0.1;
						}
						this.CurPage = NewPage;
					}
					else
					{
						Result = true;
						bBreak = true;
						break;
					}
				}

				if (false === Result || true === bBreak)
					break;

				CurY = StartY;
			}
		}


		this.MoveCursorToXY(StartX, CurY, AddToSelect);
		this.private_UpdateCursorXY(false, true);

		if (this.CurPos.RealY > StartY + 0.001)
		{
			Result = true;
			break;
		}
	}

	this.CheckEmptyElementsOnSelection = true;
	this.TurnOn_InterfaceEvents(true);
	return Result;
};
CDocument.prototype.private_MoveCursorUp = function(StartX, StartY, AddToSelect)
{
	var StartPage = this.CurPage;
	var CurY      = StartY;

	var PageH = this.Pages[this.CurPage].Height;

	this.TurnOff_InterfaceEvents();
	this.CheckEmptyElementsOnSelection = false;

	var Result = false;
	while (true)
	{
		CurY -= 0.1;

		if (CurY < 0 || this.CurPage < StartPage)
		{
			this.CurPage = StartPage;
			if (0 === this.CurPage)
			{
				Result = false;
				break;
			}
			else
			{
				this.CurPage--;
				StartY = this.Pages[this.CurPage].Height;

				var NewPage = this.CurPage;
				var bBreak  = false;
				while (true)
				{
					this.MoveCursorToXY(StartX, StartY, AddToSelect);
					this.private_UpdateCursorXY(false, true);

					if (this.CurPage > NewPage)
					{
						this.CurPage = NewPage;
						StartY -= 0.1;
					}
					else
					{
						Result = true;
						bBreak = true;
						break;
					}
				}

				if (false === Result || true === bBreak)
					break;

				CurY = StartY;
			}
		}

		this.MoveCursorToXY(StartX, CurY, AddToSelect);
		this.private_UpdateCursorXY(false, true);

		if (this.CurPos.RealY < StartY - 0.001)
		{
			Result = true;
			break;
		}
	}

	this.CheckEmptyElementsOnSelection = true;
	this.TurnOn_InterfaceEvents(true);
	return Result;
};
CDocument.prototype.private_ProcessTemplateReplacement = function(TemplateReplacementData)
{
	for (var Id in TemplateReplacementData)
	{
		this.Search(Id, {MatchCase : true}, false);
		this.SearchEngine.Replace_All(TemplateReplacementData[Id], false);
	}
};
CDocument.prototype.Reset_WordSelection = function()
{
	this.Selection.WordSelected = false;
};
CDocument.prototype.Set_WordSelection = function()
{
	this.Selection.WordSelected = true;
};
CDocument.prototype.Is_WordSelection = function()
{
	return this.Selection.WordSelected;
};
CDocument.prototype.Get_EditingType = function()
{
	return this.EditingType;
};
CDocument.prototype.Set_EditingType = function(EditingType)
{
	this.EditingType = EditingType;
};
CDocument.prototype.Is_TrackRevisions = function()
{
	return this.TrackRevisions;
};
CDocument.prototype.Get_TrackRevisionsManager = function()
{
	return this.TrackRevisionsManager;
};
CDocument.prototype.Start_SilentMode = function()
{
	this.TurnOff_Recalculate();
	this.TurnOff_InterfaceEvents();
	this.TurnOff_RecalculateCurPos();
};
CDocument.prototype.End_SilentMode = function(bUpdate)
{
	this.TurnOn_Recalculate(bUpdate);
	this.TurnOn_RecalculateCurPos(bUpdate);
	this.TurnOn_InterfaceEvents(bUpdate);
};
/**
 * Начинаем селект с текущей точки. Если селект уже есть, тогда ничего не делаем.
 */
CDocument.prototype.StartSelectionFromCurPos = function()
{
	if (true === this.IsSelectionUse())
		return true;

	this.Selection.Use   = true;
	this.Selection.Start = false;

	this.Controller.StartSelectionFromCurPos();
};
CDocument.prototype.Is_TrackingDrawingObjects = function()
{
	return this.DrawingObjects.Check_TrackObjects();
};
CDocument.prototype.Add_ChangedStyle = function(arrStylesId)
{
	for (var nIndex = 0, nCount = arrStylesId.length; nIndex < nCount; nIndex++)
	{
		this.ChangedStyles[arrStylesId[nIndex]] = true;
	}
};
CDocument.prototype.Document_UpdateStylesPanel = function()
{
	if (0 !== this.TurnOffPanelStyles)
		return;

	var bNeedUpdate = false;
	for (var StyleId in this.ChangedStyles)
	{
		bNeedUpdate = true;
		break;
	}

	this.ChangedStyles = {};

	if (true === bNeedUpdate)
	{
		editor.GenerateStyles();
	}
};
CDocument.prototype.LockPanelStyles = function()
{
	this.TurnOffPanelStyles++;
};
CDocument.prototype.UnlockPanelStyles = function(isUpdate)
{
	this.TurnOffPanelStyles = Math.max(0, this.TurnOffPanelStyles - 1);

	if (true === isUpdate)
		this.Document_UpdateStylesPanel();
};
CDocument.prototype.GetAllParagraphs = function(Props)
{
	var ParaArray = [];

	if (true === Props.OnlyMainDocument)
	{
		var Count = this.Content.length;
		for (var Index = 0; Index < Count; Index++)
		{
			var Element = this.Content[Index];
			Element.GetAllParagraphs(Props, ParaArray);
		}
	}
	else
	{
		this.SectionsInfo.GetAllParagraphs(Props, ParaArray);

		var Count = this.Content.length;
		for (var Index = 0; Index < Count; Index++)
		{
			var Element = this.Content[Index];
			Element.GetAllParagraphs(Props, ParaArray);
		}

		this.Footnotes.GetAllParagraphs(Props, ParaArray);
	}

	return ParaArray;
};
CDocument.prototype.GetAllParagraphsByNumbering = function(NumPr)
{
	return this.GetAllParagraphs({Numbering : true, NumPr : NumPr});
};
CDocument.prototype.GetAllParagraphsByStyle = function(StylesId)
{
	return this.GetAllParagraphs({Style : true, StylesId : StylesId});
};
CDocument.prototype.TurnOffHistory = function()
{
	this.History.TurnOff();
	this.TableId.TurnOff();
};
CDocument.prototype.TurnOnHistory = function()
{
	this.TableId.TurnOn();
	this.History.TurnOn();
};
CDocument.prototype.Get_SectPr = function(Index)
{
	return this.SectionsInfo.Get_SectPr(Index).SectPr;
};
CDocument.prototype.Add_ToContent = function(Pos, Item)
{
	this.Internal_Content_Add(Pos, Item);
};
CDocument.prototype.Remove_FromContent = function(Pos, Count)
{
	this.Internal_Content_Remove(Pos, Count);
};
CDocument.prototype.Concat_Paragraphs = function(Pos)
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
CDocument.prototype.Get_ElementsCount = function()
{
	return this.Content.length;
};
CDocument.prototype.Get_ElementByIndex = function(Index)
{
	return this.Content[Index];
};
CDocument.prototype.Set_FastCollaborativeEditing = function(isOn)
{
	this.CollaborativeEditing.Set_Fast(isOn);

	if (c_oAscCollaborativeMarksShowType.LastChanges === this.Api.GetCollaborativeMarksShowType())
		this.Api.SetCollaborativeMarksShowType(c_oAscCollaborativeMarksShowType.All);
};
CDocument.prototype.Continue_FastCollaborativeEditing = function()
{
	if (true === this.CollaborativeEditing.Get_GlobalLock())
		return;

	if (this.Api.isLongAction())
		return;

	if (true !== this.CollaborativeEditing.Is_Fast() || true === this.CollaborativeEditing.Is_SingleUser())
		return;

	if (true === this.IsMovingTableBorder() || true === this.Api.isStartAddShape || this.DrawingObjects.checkTrackDrawings() || this.Api.isOpenedChartFrame)
		return;

	var HaveChanges = this.History.Have_Changes(true);
	if (true !== HaveChanges && (true === this.CollaborativeEditing.Have_OtherChanges() || 0 !== this.CollaborativeEditing.getOwnLocksLength()))
	{
		// Принимаем чужие изменения. Своих нет, но функцию отсылки надо вызвать, чтобы снять локи.
		this.CollaborativeEditing.Apply_Changes();
		this.CollaborativeEditing.Send_Changes();
	}
	else if (true === HaveChanges || true === this.CollaborativeEditing.Have_OtherChanges())
	{
		this.Api.asc_Save(true);
	}

	var CurTime = new Date().getTime();
	if (true === this.NeedUpdateTargetForCollaboration && (CurTime - this.LastUpdateTargetTime > 1000))
	{
		this.NeedUpdateTargetForCollaboration = false;
		if (true !== HaveChanges)
		{
			var CursorInfo = this.History.Get_DocumentPositionBinary();
			if (null !== CursorInfo)
			{
				this.Api.CoAuthoringApi.sendCursor(CursorInfo);
				this.LastUpdateTargetTime = CurTime;
			}
		}
		else
		{
			this.LastUpdateTargetTime = CurTime;
		}
	}
};
CDocument.prototype.Save_DocumentStateBeforeLoadChanges = function()
{
	var State = {};

	State.CurPos =
	{
		X     : this.CurPos.X,
		Y     : this.CurPos.Y,
		RealX : this.CurPos.RealX,
		RealY : this.CurPos.RealY,
		Type  : this.CurPos.Type
	};

	State.Selection =
	{
		Start          : this.Selection.Start,
		Use            : this.Selection.Use,
		Flag           : this.Selection.Flag,
		UpdateOnRecalc : this.Selection.UpdateOnRecalc,
		DragDrop       : {
			Flag : this.Selection.DragDrop.Flag,
			Data : null === this.Selection.DragDrop.Data ? null : {
				X       : this.Selection.DragDrop.Data.X,
				Y       : this.Selection.DragDrop.Data.Y,
				PageNum : this.Selection.DragDrop.Data.PageNum
			}
		}
	};

	State.SingleCell = this.GetSelectedElementsInfo().Get_SingleCell();
	State.Pos        = [];
	State.StartPos   = [];
	State.EndPos     = [];

	this.Controller.SaveDocumentStateBeforeLoadChanges(State);
	this.RemoveSelection();
	return State;
};
CDocument.prototype.Load_DocumentStateAfterLoadChanges = function(State)
{
	this.CurPos.X     = State.CurPos.X;
	this.CurPos.Y     = State.CurPos.Y;
	this.CurPos.RealX = State.CurPos.RealX;
	this.CurPos.RealY = State.CurPos.RealY;
	this.Set_DocPosType(State.CurPos.Type);

	this.Selection.Start          = State.Selection.Start;
	this.Selection.Use            = State.Selection.Use;
	this.Selection.Flag           = State.Selection.Flag;
	this.Selection.UpdateOnRecalc = State.Selection.UpdateOnRecalc;
	this.Selection.DragDrop.Flag  = State.Selection.DragDrop.Flag;
	this.Selection.DragDrop.Data  = State.Selection.DragDrop.Data === null ? null : {
		X       : State.Selection.DragDrop.Data.X,
		Y       : State.Selection.DragDrop.Data.Y,
		PageNum : State.Selection.DragDrop.Data.PageNum
	};

	this.Controller.RestoreDocumentStateAfterLoadChanges(State);

	if (true === this.Selection.Use && null !== State.SingleCell && undefined !== State.SingleCell)
	{
		var Cell  = State.SingleCell;
		var Table = Cell.Get_Table();
		if (Table && true === Table.Is_UseInDocument())
		{
			Table.Set_CurCell(Cell);
			Table.RemoveSelection();
			Table.SelectTable(c_oAscTableSelectionType.Cell);
		}
	}
};
CDocument.prototype.SaveDocumentState = function()
{
	return this.Save_DocumentStateBeforeLoadChanges();
};
CDocument.prototype.LoadDocumentState = function(oState)
{
	return this.Load_DocumentStateAfterLoadChanges(oState);
};
CDocument.prototype.SetContentSelection = function(StartDocPos, EndDocPos, Depth, StartFlag, EndFlag)
{
	if ((0 === StartFlag && (!StartDocPos[Depth] || this !== StartDocPos[Depth].Class)) || (0 === EndFlag && (!EndDocPos[Depth] || this !== EndDocPos[Depth].Class)))
		return;

	var StartPos = 0, EndPos = 0;
	switch (StartFlag)
	{
		case 0 :
			StartPos = StartDocPos[Depth].Position;
			break;
		case 1 :
			StartPos = 0;
			break;
		case -1:
			StartPos = this.Content.length - 1;
			break;
	}

	switch (EndFlag)
	{
		case 0 :
			EndPos = EndDocPos[Depth].Position;
			break;
		case 1 :
			EndPos = 0;
			break;
		case -1:
			EndPos = this.Content.length - 1;
			break;
	}

	var _StartDocPos = StartDocPos, _StartFlag = StartFlag;
	if (null !== StartDocPos && true === StartDocPos[Depth].Deleted)
	{
		if (StartPos < this.Content.length)
		{
			_StartDocPos = null;
			_StartFlag   = 1;
		}
		else if (StartPos > 0)
		{
			StartPos--;
			_StartDocPos = null;
			_StartFlag   = -1;
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
			_EndFlag   = 1;
		}
		else if (EndPos > 0)
		{
			EndPos--;
			_EndDocPos = null;
			_EndFlag   = -1;
		}
		else
		{
			// Такого не должно быть
			return;
		}
	}

	this.Selection.StartPos = StartPos;
	this.Selection.EndPos   = EndPos;

	if (StartPos !== EndPos)
	{
		this.Content[StartPos].SetContentSelection(_StartDocPos, null, Depth + 1, _StartFlag, StartPos > EndPos ? 1 : -1);
		this.Content[EndPos].SetContentSelection(null, _EndDocPos, Depth + 1, StartPos > EndPos ? -1 : 1, _EndFlag);

		var _StartPos = StartPos;
		var _EndPos   = EndPos;
		var Direction = 1;

		if (_StartPos > _EndPos)
		{
			_StartPos = EndPos;
			_EndPos   = StartPos;
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
CDocument.prototype.GetContentPosition = function(bSelection, bStart, PosArray)
{
	if (undefined === PosArray)
		PosArray = [];

	var Pos = (true === bSelection ? (true === bStart ? this.Selection.StartPos : this.Selection.EndPos) : this.CurPos.ContentPos);
	PosArray.push({Class : this, Position : Pos});

	if (undefined !== this.Content[Pos] && this.Content[Pos].GetContentPosition)
		this.Content[Pos].GetContentPosition(bSelection, bStart, PosArray);

	return PosArray;
};
CDocument.prototype.SetContentPosition = function(DocPos, Depth, Flag)
{
	if (0 === Flag && (!DocPos[Depth] || this !== DocPos[Depth].Class))
		return;

	var Pos = 0;
	switch (Flag)
	{
		case 0 :
			Pos = DocPos[Depth].Position;
			break;
		case 1 :
			Pos = 0;
			break;
		case -1:
			Pos = this.Content.length - 1;
			break;
	}

	var _DocPos = DocPos, _Flag = Flag;
	if (null !== DocPos && true === DocPos[Depth].Deleted)
	{
		if (Pos < this.Content.length)
		{
			_DocPos = null;
			_Flag   = 1;
		}
		else if (Pos > 0)
		{
			Pos--;
			_DocPos = null;
			_Flag   = -1;
		}
		else
		{
			// Такого не должно быть
			return;
		}
	}

	this.CurPos.ContentPos = Pos;

	if (this.Content[Pos])
		this.Content[Pos].SetContentPosition(_DocPos, Depth + 1, _Flag);
};
CDocument.prototype.GetDocumentPositionFromObject = function(PosArray)
{
	if (!PosArray)
		PosArray = [];

	return PosArray;
};
CDocument.prototype.SetSelectionByContentPositions = function(StartDocPos, EndDocPos)
{
	this.RemoveSelection();

	this.Selection.Use   = true;
	this.Selection.Start = false;
	this.Selection.Flag  = selectionflag_Common;

	this.SetContentSelection(StartDocPos, EndDocPos, 0, 0, 0);
};
CDocument.prototype.Get_CursorLogicPosition = function()
{
	var nDocPosType = this.Get_DocPosType();
	if (docpostype_HdrFtr === nDocPosType)
	{
		var HdrFtr = this.HdrFtr.Get_CurHdrFtr();
		if (HdrFtr)
		{
			return this.private_GetLogicDocumentPosition(HdrFtr.Get_DocumentContent());
		}
	}
	else if (docpostype_Footnotes === nDocPosType)
	{
		var oFootnote = this.Footnotes.GetCurFootnote();
		if (oFootnote)
			return this.private_GetLogicDocumentPosition(oFootnote);
	}
	else
	{
		return this.private_GetLogicDocumentPosition(this);
	}

	return null;
};
CDocument.prototype.private_GetLogicDocumentPosition = function(LogicDocument)
{
	if (!LogicDocument)
		return null;

	if (docpostype_DrawingObjects === LogicDocument.Get_DocPosType())
	{
		var ParaDrawing    = this.DrawingObjects.getMajorParaDrawing();
		var DrawingContent = this.DrawingObjects.getTargetDocContent();
		if (!ParaDrawing)
			return null;

		if (DrawingContent)
		{
			return DrawingContent.GetContentPosition(DrawingContent.IsSelectionUse(), false);
		}
		else
		{
			var Run = ParaDrawing.Get_Run();
			if (null === Run)
				return null;

			var DrawingInRunPos = Run.Get_DrawingObjectSimplePos(ParaDrawing.Get_Id());
			if (-1 === DrawingInRunPos)
				return null;

			var DocPos = [{Class : Run, Position : DrawingInRunPos}];
			Run.GetDocumentPositionFromObject(DocPos);
			return DocPos;
		}
	}
	else
	{
		return LogicDocument.GetContentPosition(LogicDocument.IsSelectionUse(), false);
	}
};
CDocument.prototype.Get_DocumentPositionInfoForCollaborative = function()
{
	var DocPos = this.Get_CursorLogicPosition();
	if (!DocPos || DocPos.length <= 0)
		return null;

	var Last = DocPos[DocPos.length - 1];
	if (!(Last.Class instanceof ParaRun))
		return null;

	return Last;
};
CDocument.prototype.Update_ForeignCursor = function(CursorInfo, UserId, Show, UserShortId)
{
	if (!this.Api.User)
		return;

	if (UserId === this.Api.CoAuthoringApi.getUserConnectionId())
		return;

	// "" - это означает, что курсор нужно удалить
	if (!CursorInfo || "" === CursorInfo)
	{
		this.Remove_ForeignCursor(UserId);
		return;
	}

	var Changes = new AscCommon.CCollaborativeChanges();
	var Reader  = Changes.GetStream(CursorInfo, 0, CursorInfo.length);

	var RunId    = Reader.GetString2();
	var InRunPos = Reader.GetLong();

	var Run = this.TableId.Get_ById(RunId);
	if (!Run)
	{
		this.Remove_ForeignCursor(UserId);
		return;
	}

	var CursorPos = [{Class : Run, Position : InRunPos}];
	Run.GetDocumentPositionFromObject(CursorPos);
	this.CollaborativeEditing.Add_ForeignCursor(UserId, CursorPos, UserShortId);

	if (true === Show)
		this.CollaborativeEditing.Update_ForeignCursorPosition(UserId, Run, InRunPos, true);
};
CDocument.prototype.Remove_ForeignCursor = function(UserId)
{
	this.CollaborativeEditing.Remove_ForeignCursor(UserId);
};
CDocument.prototype.private_UpdateTargetForCollaboration = function()
{
	this.NeedUpdateTargetForCollaboration = true;
};
CDocument.prototype.Get_HdrFtr = function()
{
	return this.HdrFtr;
};
CDocument.prototype.Get_DrawingDocument = function()
{
	return this.DrawingDocument;
};
CDocument.prototype.Get_Api = function()
{
	return this.Api;
};
CDocument.prototype.Get_IdCounter = function()
{
	return this.IdCounter;
};
CDocument.prototype.Get_TableId = function()
{
	return this.TableId;
};
CDocument.prototype.Get_History = function()
{
	return this.History;
};
CDocument.prototype.Get_CollaborativeEditing = function()
{
	return this.CollaborativeEditing;
};
CDocument.prototype.private_CorrectDocumentPosition = function()
{
	if (this.CurPos.ContentPos < 0 || this.CurPos.ContentPos >= this.Content.length)
	{
		this.RemoveSelection();
		if (this.CurPos.ContentPos < 0)
		{
			this.CurPos.ContentPos = 0;
			this.Content[0].MoveCursorToStartPos(false);
		}
		else
		{
			this.CurPos.ContentPos = this.Content.length - 1;
			this.Content[this.CurPos.ContentPos].MoveCursorToEndPos(false);
		}
	}
};
CDocument.prototype.private_ToggleParagraphAlignByHotkey = function(Align)
{
	var SelectedInfo = this.GetSelectedElementsInfo();
	var Math         = SelectedInfo.Get_Math();
	if (null !== Math && true !== Math.Is_Inline())
	{
		var MathAlign = Math.Get_Align();
		if (Align !== MathAlign)
		{
			if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
			{
				this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetParagraphAlignHotKey);
				Math.Set_Align(Align);
				this.Recalculate();
				this.Document_UpdateInterfaceState();
			}
		}
	}
	else
	{
		var ParaPr = this.GetCalculatedParaPr();
		if (null != ParaPr)
		{
			if (false === this.Document_Is_SelectionLocked(AscCommon.changestype_Paragraph_Properties))
			{
				this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetParagraphAlignHotKey);
				this.SetParagraphAlign(ParaPr.Jc === Align ? (Align === align_Left ? AscCommon.align_Justify : align_Left) : Align);
				this.Document_UpdateInterfaceState();
			}
		}
	}
};
CDocument.prototype.Is_ShowParagraphMarks = function()
{
	return this.Api.ShowParaMarks;
};
CDocument.prototype.Set_ShowParagraphMarks = function(isShow, isRedraw)
{
	this.Api.ShowParaMarks = isShow;

	if (true === isRedraw)
	{
		this.DrawingDocument.ClearCachePages();
		this.DrawingDocument.FirePaint();
	}
};
CDocument.prototype.Get_StyleNameById = function(StyleId)
{
	if (!this.Styles)
		return "";

	var Style = this.Styles.Get(StyleId);
	if (!Style)
		return "";

	return Style.Get_Name();
};
CDocument.prototype.private_GetElementPageIndex = function(ElementPos, PageIndex, ColumnIndex, ColumnsCount)
{
	var Element = this.Content[ElementPos];
	if (!Element)
		return 0;

	var StartPage   = Element.Get_StartPage_Relative();
	var StartColumn = Element.Get_StartColumn();

	return ColumnIndex - StartColumn + (PageIndex - StartPage) * ColumnsCount;
};
CDocument.prototype.private_GetElementPageIndexByXY = function(ElementPos, X, Y, PageIndex)
{
	var Element = this.Content[ElementPos];
	if (!Element)
		return 0;

	var Page = this.Pages[PageIndex];
	if (!Page)
		return 0;

	var PageSection = null;
	for (var SectionIndex = 0, SectionsCount = Page.Sections.length; SectionIndex < SectionsCount; ++SectionIndex)
	{
		if (Page.Sections[SectionIndex].Pos <= ElementPos && ElementPos <= Page.Sections[SectionIndex].EndPos)
		{
			PageSection = Page.Sections[SectionIndex];
			break;
		}
	}

	if (!PageSection)
		return 0;

	var ElementStartPage   = Element.Get_StartPage_Relative();
	var ElementStartColumn = Element.Get_StartColumn();
	var ElementPagesCount  = Element.Get_PagesCount();

	var ColumnsCount = PageSection.Columns.length;
	var StartColumn  = 0;
	var EndColumn    = ColumnsCount - 1;

	if (PageIndex === ElementStartPage)
	{
		StartColumn = Element.Get_StartColumn();
		EndColumn   = Math.min(ElementStartColumn + ElementPagesCount - 1, ColumnsCount - 1);
	}
	else
	{
		StartColumn = 0;
		EndColumn   = Math.min(ElementPagesCount - ElementStartColumn + (PageIndex - ElementStartPage) * ColumnsCount, ColumnsCount - 1);
	}

	// TODO: Разобраться с ситуацией, когда пустые колонки стоят не только в конце
	while (true === PageSection.Columns[EndColumn].Empty && EndColumn > StartColumn)
		EndColumn--;

	var ResultColumn = EndColumn;
	for (var ColumnIndex = StartColumn; ColumnIndex < EndColumn; ++ColumnIndex)
	{
		if (X < (PageSection.Columns[ColumnIndex].XLimit + PageSection.Columns[ColumnIndex + 1].X) / 2)
		{
			ResultColumn = ColumnIndex;
			break;
		}
	}

	return this.private_GetElementPageIndex(ElementPos, PageIndex, ResultColumn, ColumnsCount);
};
CDocument.prototype.Get_DocumentPagePositionByContentPosition = function(ContentPosition)
{
	if (!ContentPosition)
		return null;

	var Para    = null;
	var ParaPos = 0;
	var Count   = ContentPosition.length;
	for (; ParaPos < Count; ++ParaPos)
	{
		var Element = ContentPosition[ParaPos].Class;
		if (Element instanceof Paragraph)
		{
			Para = Element;
			break;
		}
	}

	if (!Para)
		return null;

	var ParaContentPos = new CParagraphContentPos();
	for (var Pos = ParaPos; Pos < Count; ++Pos)
	{
		ParaContentPos.Update(ContentPosition[Pos].Position, Pos - ParaPos);
	}

	var ParaPos = Para.Get_ParaPosByContentPos(ParaContentPos);
	if (!ParaPos)
		return;

	var Result    = new CDocumentPagePosition();
	Result.Page   = Para.Get_AbsolutePage(ParaPos.Page);
	Result.Column = Para.Get_AbsoluteColumn(ParaPos.Page);

	return Result;
};
CDocument.prototype.private_GetPageSectionByContentPosition = function(PageIndex, ContentPosition)
{
	var Page = this.Pages[PageIndex];
	if (!Page || !Page.Sections || Page.Sections.length <= 1)
		return 0;

	var SectionIndex = 0;
	for (var SectionsCount = Page.Sections.length; SectionIndex < SectionsCount; ++SectionIndex)
	{
		var Section = Page.Sections[SectionIndex];
		if (Section.Pos <= ContentPosition && ContentPosition <= Section.EndPos)
			break;
	}

	if (SectionIndex >= Page.Sections.length)
		return 0;

	return SectionIndex;
};
CDocument.prototype.Update_ColumnsMarkupFromRuler = function(NewMarkup)
{
	var SectPr = NewMarkup.SectPr;
	if (!SectPr)
		return;

	if (false === this.Document_Is_SelectionLocked(AscCommon.changestype_Document_SectPr))
	{
		this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetColumnsFromRuler);

		SectPr.Set_Columns_EqualWidth(NewMarkup.EqualWidth);
		SectPr.Set_PageMargins(NewMarkup.X, undefined, SectPr.Get_PageWidth() - NewMarkup.R, undefined);
		if (false === NewMarkup.EqualWidth)
		{
			for (var Index = 0, Count = NewMarkup.Cols.length; Index < Count; ++Index)
			{
				SectPr.Set_Columns_Col(Index, NewMarkup.Cols[Index].W, NewMarkup.Cols[Index].Space);
			}
		}
		else
		{
			SectPr.Set_Columns_Space(NewMarkup.Space);
			SectPr.Set_Columns_Num(NewMarkup.Num);
		}

		this.Recalculate();
		this.Document_UpdateSelectionState();
		this.Document_UpdateInterfaceState();
		this.Document_UpdateRulersState();
	}
};
CDocument.prototype.Set_ColumnsProps = function(ColumnsProps)
{
	if (this.IsSelectionUse())
	{
		if (docpostype_DrawingObjects === this.Get_DocPosType())
			return;

		// К селекту мы применяем колонки не так как ворд.
		// Элементы попавшие в селект полностью входят в  новую секцию, даже если они выделены частично.
		
		var nStartPos  = this.Selection.StartPos;
		var nEndPos    = this.Selection.EndPos;
		var nDirection = 1;

		if (nEndPos < nStartPos)
		{
			nStartPos  = this.Selection.EndPos;
			nEndPos    = this.Selection.StartPos;
			nDirection = -1;
		}

		var oStartSectPr = this.SectionsInfo.Get_SectPr(nStartPos).SectPr;
		var oEndSectPr   = this.SectionsInfo.Get_SectPr(nEndPos).SectPr;
		if (!oStartSectPr || !oEndSectPr)
			return;

		if (this.Document_Is_SelectionLocked(AscCommon.changestype_Document_SectPr))
			return;

		this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetColumnsProps);

		var oEndParagraph = null;
		if (type_Paragraph !== this.Content[nEndPos].GetType())
		{
			oEndParagraph = new Paragraph(this.DrawingDocument, this);
			this.Add_ToContent(nEndPos + 1, oEndParagraph);
		}
		else
		{
			oEndParagraph = this.Content[nEndPos];
		}

		if (nStartPos > 0
			&& (type_Paragraph !== this.Content[nStartPos - 1].GetType()
			|| !this.Content[nStartPos - 1].Get_SectionPr()))
		{
			var oSectPr = new CSectionPr(this);
			oSectPr.Copy(oStartSectPr, false);

			var oStartParagraph = new Paragraph(this.DrawingDocument, this);
			this.Add_ToContent(nStartPos, oStartParagraph);
			oStartParagraph.Set_SectionPr(oSectPr, true);

			nStartPos++;
			nEndPos++;
		}

		oEndSectPr.Set_Type(c_oAscSectionBreakType.Continuous);
		var oSectPr = new CSectionPr(this);
		oSectPr.Copy(oEndSectPr, false);
		oEndParagraph.Set_SectionPr(oSectPr, true);

		oSectPr.SetColumnProps(ColumnsProps);

		for (var nIndex = nStartPos; nIndex < nEndPos; ++nIndex)
		{
			var oElement = this.Content[nIndex];
			if (type_Paragraph === oElement.GetType())
			{
				var oCurSectPr = oElement.Get_SectionPr();
				if (oCurSectPr)
					oCurSectPr.SetColumnProps(ColumnsProps);
			}
		}

		if (nDirection >= 0)
		{
			this.Selection.StartPos = nStartPos;
			this.Selection.EndPos   = nEndPos;
		}
		else
		{
			this.Selection.StartPos = nEndPos;
			this.Selection.EndPos   = nStartPos;
		}

		this.Recalculate();
		this.Document_UpdateSelectionState();
		this.Document_UpdateInterfaceState();
		this.Document_UpdateRulersState();
	}
	else
	{
		var CurPos = this.CurPos.ContentPos;
		var SectPr = this.SectionsInfo.Get_SectPr(CurPos).SectPr;

		if (!SectPr)
			return;

		if (false === this.Document_Is_SelectionLocked(AscCommon.changestype_Document_SectPr))
		{
			this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetColumnsProps);

			SectPr.SetColumnProps(ColumnsProps);

			this.Recalculate();
			this.Document_UpdateSelectionState();
			this.Document_UpdateInterfaceState();
			this.Document_UpdateRulersState();
		}
	}
};
CDocument.prototype.Get_TopDocumentContent = function()
{
	return this;
};
CDocument.prototype.private_RecalculateNumbering = function(Elements)
{
	if (true === AscCommon.g_oIdCounter.m_bLoad)
		return;

	for (var Index = 0, Count = Elements.length; Index < Count; ++Index)
	{
		var Element = Elements[Index];
		if (type_Paragraph === Element.Get_Type())
			this.History.Add_RecalcNumPr(Element.Numbering_Get());
		else if (type_Paragraph === Element.Get_Type())
		{
			var ParaArray = [];
			Element.GetAllParagraphs({All : true}, ParaArray);

			for (var ParaIndex = 0, ParasCount = ParaArray.length; ParaIndex < ParasCount; ++ParaIndex)
			{
				var Para = ParaArray[ParaIndex];
				this.History.Add_RecalcNumPr(Element.Numbering_Get());
			}
		}
	}
};
CDocument.prototype.Set_SectionProps = function(Props)
{
	var CurPos = this.CurPos.ContentPos;
	var SectPr = this.SectionsInfo.Get_SectPr(CurPos).SectPr;

	if (SectPr && false === this.Document_Is_SelectionLocked(AscCommon.changestype_Document_SectPr))
	{
		this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetSectionProps);

		if (undefined !== Props.get_W() || undefined !== Props.get_H())
		{
			var PageW = undefined !== Props.get_W() ? Props.get_W() : SectPr.Get_PageWidth();
			var PageH = undefined !== Props.get_H() ? Props.get_H() : SectPr.Get_PageHeight();
			SectPr.Set_PageSize(PageW, PageH);
		}

		if (undefined !== Props.get_Orientation())
		{
			SectPr.Set_Orientation(Props.get_Orientation(), false);
		}

		if (undefined !== Props.get_LeftMargin() || undefined !== Props.get_TopMargin() || undefined !== Props.get_RightMargin() || undefined !== Props.get_BottomMargin())
		{
			// Внутри функции идет разруливания, если какое то значение undefined
			SectPr.Set_PageMargins(Props.get_LeftMargin(), Props.get_TopMargin(), Props.get_RightMargin(), Props.get_BottomMargin());
		}

		if (undefined !== Props.get_HeaderDistance())
		{
			SectPr.Set_PageMargins_Header(Props.get_HeaderDistance());
		}

		if (undefined !== Props.get_FooterDistance())
		{
			SectPr.Set_PageMargins_Footer(Props.get_FooterDistance());
		}

		if (true === this.History.Is_LastPointEmpty())
		{
			this.History.Remove_LastPoint();
		}
		else
		{
			this.Recalculate();
			this.Document_UpdateSelectionState();
			this.Document_UpdateInterfaceState();
			this.Document_UpdateRulersState();
		}
	}
};
CDocument.prototype.Get_SectionProps = function()
{
	var CurPos = this.CurPos.ContentPos;
	var SectPr = this.SectionsInfo.Get_SectPr(CurPos).SectPr;

	return new Asc.CDocumentSectionProps(SectPr);
};
CDocument.prototype.Get_FirstParagraph = function()
{
	if (type_Paragraph == this.Content[0].GetType())
		return this.Content[0];
	else if (type_Table == this.Content[0].GetType())
		return this.Content[0].Get_FirstParagraph();

	return null;
};
/**
 * Обработчик нажатия кнопки IncreaseIndent в меню.
 */
CDocument.prototype.IncreaseIndent = function()
{
	if (false === this.Document_Is_SelectionLocked(AscCommon.changestype_Paragraph_Properties))
	{
		this.Create_NewHistoryPoint(AscDFH.historydescription_Document_IncParagraphIndent);
		this.IncreaseDecreaseIndent(true);
		this.Document_UpdateSelectionState();
		this.Document_UpdateInterfaceState();
		this.Recalculate();
	}
};
/**
 * Обработчик нажатия кнопки DecreaseIndent в меню.
 */
CDocument.prototype.DecreaseIndent = function()
{
	if (false === this.Document_Is_SelectionLocked(AscCommon.changestype_Paragraph_Properties))
	{
		this.Create_NewHistoryPoint(AscDFH.historydescription_Document_DecParagraphIndent);
		this.IncreaseDecreaseIndent(false);
		this.Document_UpdateSelectionState();
		this.Document_UpdateInterfaceState();
		this.Recalculate();
	}
};
/**
 * Получаем размеры текущей колонки (используется при вставке изображения).
 */
CDocument.prototype.GetColumnSize = function()
{
	return this.Controller.GetColumnSize();
};
CDocument.prototype.private_OnSelectionEnd = function()
{
	this.Api.sendEvent("asc_onSelectionEnd");
};
CDocument.prototype.AddPageCount = function()
{
	if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
	{
		this.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddPageCount);
		this.AddToParagraph(new ParaPageCount(this.Pages.length));
	}
};
//----------------------------------------------------------------------------------------------------------------------
// Settings
//----------------------------------------------------------------------------------------------------------------------
CDocument.prototype.Get_CompatibilityMode = function()
{
	return this.Settings.CompatibilityMode;
};
//----------------------------------------------------------------------------------------------------------------------
// Math
//----------------------------------------------------------------------------------------------------------------------
CDocument.prototype.Set_MathProps = function(MathProps)
{
	var SelectedInfo = this.GetSelectedElementsInfo();
	if (null !== SelectedInfo.Get_Math() && false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
	{
		this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetMathProps);

		var ParaMath = SelectedInfo.Get_Math();
		ParaMath.Set_MenuProps(MathProps);

		this.Recalculate();
		this.Document_UpdateSelectionState();
		this.Document_UpdateInterfaceState();
	}
};
//----------------------------------------------------------------------------------------------------------------------
// Statistics (Функции для работы со статистикой)
//----------------------------------------------------------------------------------------------------------------------
CDocument.prototype.Statistics_Start = function()
{
	this.Statistics.Start();
};
CDocument.prototype.Statistics_GetParagraphsInfo = function()
{
	var Count   = this.Content.length;
	var CurPage = this.Statistics.CurPage;

	var Index    = 0;
	var CurIndex = 0;
	for (Index = this.Statistics.StartPos; Index < Count; ++Index, ++CurIndex)
	{
		var Element = this.Content[Index];
		Element.CollectDocumentStatistics(this.Statistics);

		if (CurIndex > 20)
		{
			this.Statistics.Next_ParagraphsInfo(Index + 1);
			break;
		}
	}

	if (Index >= Count)
		this.Statistics.Stop_ParagraphsInfo();
};
CDocument.prototype.Statistics_GetPagesInfo = function()
{
	this.Statistics.Update_Pages(this.Pages.length);

	if (null !== this.FullRecalc.Id)
	{
		this.Statistics.Next_PagesInfo();
	}
	else
	{
		for (var CurPage = 0, PagesCount = this.Pages.length; CurPage < PagesCount; ++CurPage)
		{
			this.DrawingObjects.documentStatistics(CurPage, this.Statistics);
		}

		this.Statistics.Stop_PagesInfo();
	}
};
CDocument.prototype.Statistics_Stop = function()
{
	this.Statistics.Stop();
};
//----------------------------------------------------------------------------------------------------------------------
// Private
//----------------------------------------------------------------------------------------------------------------------
CDocument.prototype.EndPreview_MailMergeResult = function(){};
CDocument.prototype.Continue_TrackRevisions = function(){};
CDocument.prototype.Set_TrackRevisions = function(bTrack){};
//----------------------------------------------------------------------------------------------------------------------
// Функции для работы с составным вводом
//----------------------------------------------------------------------------------------------------------------------
/**
 * Сообщаем о начале составного ввода текста.
 * @returns {boolean} Начался или нет составной ввод.
 */
CDocument.prototype.Begin_CompositeInput = function()
{
	if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content, null, true))
	{
		this.Create_NewHistoryPoint(AscDFH.historydescription_Document_CompositeInput);
        this.DrawingObjects.CreateDocContent();
		this.DrawingDocument.TargetStart();
		this.DrawingDocument.TargetShow();

		if (true === this.IsSelectionUse())
			this.Remove(1, true, false, true);

		var oPara = this.GetCurrentParagraph();
		if (!oPara)
		{
			this.History.Remove_LastPoint();
			return false;
		}

		var oRun = oPara.Get_ElementByPos(oPara.Get_ParaContentPos(false, false));
		if (!oRun || !(oRun instanceof ParaRun))
		{
			this.History.Remove_LastPoint();
			return false;
		}

		this.CompositeInput = {
			Run     : oRun,
			Pos     : oRun.State.ContentPos,
			Length  : 0,
			CanUndo : true
		};

		oRun.Set_CompositeInput(this.CompositeInput);

		return true;
	}

	return false;
};
CDocument.prototype.Replace_CompositeText = function(arrCharCodes)
{
	if (null === this.CompositeInput)
		return;

	this.Create_NewHistoryPoint(AscDFH.historydescription_Document_CompositeInputReplace);
	this.Start_SilentMode();
	this.private_RemoveCompositeText(this.CompositeInput.Length);
	for (var nIndex = 0, nCount = arrCharCodes.length; nIndex < nCount; ++nIndex)
	{
		this.private_AddCompositeText(arrCharCodes[nIndex]);
	}
	this.End_SilentMode(false);

	this.Recalculate();
	this.Document_UpdateSelectionState();
	this.Document_UpdateUndoRedoState();

	if (!this.History.CheckUnionLastPoints())
		this.CompositeInput.CanUndo = false;
};
CDocument.prototype.Set_CursorPosInCompositeText = function(nPos)
{
	if (null === this.CompositeInput)
		return;

	var oRun = this.CompositeInput.Run;

	var nInRunPos = Math.max(Math.min(this.CompositeInput.Pos + nPos, this.CompositeInput.Pos + this.CompositeInput.Length, oRun.Content.length), this.CompositeInput.Pos);
	oRun.State.ContentPos = nInRunPos;
	this.Document_UpdateSelectionState();
};
CDocument.prototype.Get_CursorPosInCompositeText = function()
{
	if (null === this.CompositeInput)
		return 0;

	var oRun = this.CompositeInput.Run;
	var nInRunPos = oRun.State.ContentPos;
	var nPos = Math.min(this.CompositeInput.Length, Math.max(0, nInRunPos - this.CompositeInput.Pos));
	return nPos;
};
CDocument.prototype.End_CompositeInput = function()
{
	if (null === this.CompositeInput)
		return;

	var nLen = this.CompositeInput.Length;
	
	var oRun = this.CompositeInput.Run;
	oRun.Set_CompositeInput(null);
	
	if (0 === nLen && true === this.History.CanRemoveLastPoint() && true === this.CompositeInput.CanUndo)
	{
		this.Document_Undo();
		this.History.Clear_Redo();
	}

	this.CompositeInput = null;

	this.Document_UpdateInterfaceState();

	this.DrawingDocument.ClearCachePages();
	this.DrawingDocument.FirePaint();
};
CDocument.prototype.Get_MaxCursorPosInCompositeText = function()
{
	if (null === this.CompositeInput)
		return 0;

	return this.CompositeInput.Length;
};
CDocument.prototype.private_AddCompositeText = function(nCharCode)
{
	var oRun = this.CompositeInput.Run;
	var nPos = this.CompositeInput.Pos + this.CompositeInput.Length;
	var oChar;

	if (para_Math_Run === oRun.Type)
	{
		oChar = new CMathText();
		oChar.add(nCharCode);
	}
	else
	{
		if (32 == nCharCode || 12288 == nCharCode)
		{
			oChar = new ParaSpace();
		}
		else
		{
			oChar = new ParaText();
			oChar.Set_CharCode(nCharCode);
		}
	}

	oRun.Add_ToContent(nPos, oChar, true);
	this.CompositeInput.Length++;

	this.Recalculate();
	this.Document_UpdateSelectionState();
};
CDocument.prototype.private_RemoveCompositeText = function(nCount)
{
	var oRun = this.CompositeInput.Run;
	var nPos = this.CompositeInput.Pos + this.CompositeInput.Length;

	var nDelCount = Math.max(0, Math.min(nCount, this.CompositeInput.Length, oRun.Content.length, nPos));
	oRun.Remove_FromContent(nPos - nDelCount, nDelCount, true);
	this.CompositeInput.Length -= nDelCount;

	this.Recalculate();
	this.Document_UpdateSelectionState();
};
CDocument.prototype.Check_CompositeInputRun = function()
{
	if (null === this.CompositeInput)
		return;

	var oRun = this.CompositeInput.Run;
	if (true !== oRun.Is_UseInDocument())
		AscCommon.g_inputContext.externalEndCompositeInput();
};
CDocument.prototype.Is_CursorInsideCompositeText = function()
{
	if (null === this.CompositeInput)
		return false;

	var oCurrentParagraph = this.GetCurrentParagraph();
	if (!oCurrentParagraph)
		return false;

	var oParaPos   = oCurrentParagraph.Get_ParaContentPos(false, false, false);
	var arrClasses = oCurrentParagraph.Get_ClassesByPos(oParaPos);

	if (arrClasses.length <= 0 || arrClasses[arrClasses.length - 1] !== this.CompositeInput.Run)
		return false;

	var nInRunPos = oParaPos.Get(oParaPos.Get_Depth());
	if (nInRunPos >= this.CompositeInput.Pos && nInRunPos <= this.CompositeInput.Pos + this.CompositeInput.Length)
		return true;

	return false;
};
//----------------------------------------------------------------------------------------------------------------------
// Функции для работы со сносками
//----------------------------------------------------------------------------------------------------------------------
/**
 * Переходим к редактированию сносок на заданной странице. Если сносок на заданной странице нет, тогда ничего не делаем.
 * @param {number} nPageIndex
 * @returns {boolean}
 */
CDocument.prototype.GotoFootnotesOnPage = function(nPageIndex)
{
	if (this.Footnotes.IsEmptyPage(nPageIndex))
		return false;

	this.Set_DocPosType(docpostype_Footnotes);
	this.Footnotes.GotoPage(nPageIndex);
	this.Document_UpdateSelectionState();

	return true;
};
CDocument.prototype.AddFootnote = function(sText)
{
	var nDocPosType = this.Get_DocPosType();
	if (docpostype_Content !== nDocPosType && docpostype_Footnotes !== nDocPosType)
		return;

	if (false === this.Document_Is_SelectionLocked(changestype_Paragraph_Content))
	{
		this.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddFootnote);

		var nDocPosType = this.Get_DocPosType();
		if (docpostype_Content === nDocPosType)
		{
			var oFootnote = this.Footnotes.CreateFootnote();
			oFootnote.AddDefaultFootnoteContent(sText);

			if (true === this.IsSelectionUse())
			{
				this.MoveCursorRight(false, false, false);
				this.RemoveSelection();
			}

			if (sText)
				this.AddToParagraph(new ParaFootnoteReference(oFootnote, sText));
			else
				this.AddToParagraph(new ParaFootnoteReference(oFootnote));

			this.Set_DocPosType(docpostype_Footnotes);
			this.Footnotes.Set_CurrentElement(true, 0, oFootnote);
		}
		else if (docpostype_Footnotes === nDocPosType)
		{
			this.Footnotes.AddFootnoteRef();
			this.Recalculate();
		}
	}
};
CDocument.prototype.RemoveAllFootnotes = function()
{
	var nDocPosType = this.Get_DocPosType();

	var oEngine = new CDocumentFootnotesRangeEngine(true);
	oEngine.Init(null, null);

	var arrParagraphs = this.GetAllParagraphs({OnlyMainDocument : true, All : true});
	for (var nIndex = 0, nCount = arrParagraphs.length; nIndex < nCount; ++nIndex)
	{
		arrParagraphs[nIndex].Get_FootnotesList(oEngine);
	}

	var arrFootnotes  = oEngine.GetRange();
	var arrParagraphs = oEngine.GetParagraphs();
	var arrRuns       = oEngine.GetRuns();
	var arrRefs       = oEngine.GetRefs();

	if (arrRuns.length !== arrRefs.length || arrFootnotes.length !== arrRuns.length)
		return;

	if (false === this.Document_Is_SelectionLocked(changestype_None, { Type : changestype_2_ElementsArray_and_Type, Elements : arrParagraphs, CheckType : changestype_Paragraph_Content }, true))
	{
		this.Create_NewHistoryPoint(AscDFH.historydescription_Document_RemoveAllFootnotes);

		for (var nIndex = 0, nCount = arrFootnotes.length; nIndex < nCount; ++nIndex)
		{
			var oRef = arrRefs[nIndex];
			var oRun = arrRuns[nIndex];

			oRun.RemoveElement(oRef);
		}

		this.Recalculate();

		if (docpostype_Footnotes === nDocPosType)
		{
			this.CurPos.Type = docpostype_Content;
			if (arrRuns.length > 0)
				arrRuns[0].Make_ThisElementCurrent();
		}
	}
};
CDocument.prototype.GotoFootnote = function(isNext)
{
	var nDocPosType = this.Get_DocPosType();

	if (docpostype_Footnotes === nDocPosType)
	{
		if (isNext)
			this.Footnotes.GotoNextFootnote();
		else
			this.Footnotes.GotoPrevFootnote();

		this.Document_UpdateSelectionState();
		this.Document_UpdateInterfaceState();

		return;
	}

	if (docpostype_HdrFtr == this.CurPos.Type)
	{
		this.EndHdrFtrEditing(true);
	}
	else if (docpostype_DrawingObjects === nDocPosType)
	{
		this.DrawingObjects.resetSelection2();
		this.private_UpdateCursorXY(true, true);

		this.CurPos.Type = docpostype_Content;

		this.Document_UpdateInterfaceState();
		this.Document_UpdateSelectionState();
	}

	return this.GotoFootnoteRef(isNext, true);
};
CDocument.prototype.GetFootnotesController = function()
{
	return this.Footnotes;
};
CDocument.prototype.SetFootnotePr = function(oFootnotePr, bApplyToAll)
{
	var nNumStart   = oFootnotePr.get_NumStart();
	var nNumRestart = oFootnotePr.get_NumRestart();
	var nNumFormat  = oFootnotePr.get_NumFormat();
	var nPos        = oFootnotePr.get_Pos();
	if (false === this.Document_Is_SelectionLocked(AscCommon.changestype_Document_SectPr))
	{
		this.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetFootnotePr);

		if (bApplyToAll)
		{
			for (var nIndex = 0, nCount = this.SectionsInfo.Get_SectionsCount(); nIndex < nCount; ++nIndex)
			{
				var oSectPr = this.SectionsInfo.Get_SectPr2(nIndex).SectPr;
				if (undefined !== nNumStart)
					oSectPr.SetFootnoteNumStart(nNumStart);

				if (undefined !== nNumRestart)
					oSectPr.SetFootnoteNumRestart(nNumRestart);

				if (undefined !== nNumFormat)
					oSectPr.SetFootnoteNumFormat(nNumFormat);

				if (undefined !== nPos)
					oSectPr.SetFootnotePos(nPos);
			}
		}
		else
		{
			var oSectPr = this.GetCurrentSectionPr();
			if (undefined !== nNumStart)
				oSectPr.SetFootnoteNumStart(nNumStart);

			if (undefined !== nNumRestart)
				oSectPr.SetFootnoteNumRestart(nNumRestart);

			if (undefined !== nNumFormat)
				oSectPr.SetFootnoteNumFormat(nNumFormat);

			if (undefined !== nPos)
				oSectPr.SetFootnotePos(nPos);
		}

		this.Recalculate();
	}
};
CDocument.prototype.GetFootnotePr = function()
{
	var oSectPr     = this.GetCurrentSectionPr();
	var oFootnotePr = new Asc.CAscFootnotePr();
	oFootnotePr.put_Pos(oSectPr.GetFootnotePos());
	oFootnotePr.put_NumStart(oSectPr.GetFootnoteNumStart());
	oFootnotePr.put_NumRestart(oSectPr.GetFootnoteNumRestart());
	oFootnotePr.put_NumFormat(oSectPr.GetFootnoteNumFormat());
	return oFootnotePr;
};
CDocument.prototype.IsCursorInFootnote = function()
{
	return (docpostype_Footnotes === this.Get_DocPosType() ? true : false);
};
CDocument.prototype.TurnOffCheckChartSelection = function()
{
	if (this.DrawingObjects)
	{
		this.DrawingObjects.TurnOffCheckChartSelection();
	}
};
CDocument.prototype.TurnOnCheckChartSelection = function()
{
	if (this.DrawingObjects)
	{
		this.DrawingObjects.TurnOnCheckChartSelection();
	}
};
//----------------------------------------------------------------------------------------------------------------------
// Функции, которые вызываются из CLogicDocumentController
//----------------------------------------------------------------------------------------------------------------------
CDocument.prototype.controller_CanUpdateTarget = function()
{
	if (null != this.FullRecalc.Id && this.FullRecalc.StartIndex < this.CurPos.ContentPos)
	{
		return false;
	}
	else if (null !== this.FullRecalc.Id && this.FullRecalc.StartIndex === this.CurPos.ContentPos)
	{
		var nPos         = (true === this.Selection.Use && selectionflag_Numbering !== this.Selection.Flag ? this.Selection.EndPos : this.CurPos.ContentPos)
		var oElement     = this.Content[nPos];
		var nElementPage = this.private_GetElementPageIndex(nPos, this.FullRecalc.PageIndex, this.FullRecalc.ColumnIndex, oElement.Get_ColumnsCount());
		return oElement.CanUpdateTarget(nElementPage);
	}

	return true;
};
CDocument.prototype.controller_RecalculateCurPos = function()
{
	if (this.controller_CanUpdateTarget())
	{
		var nPos = (true === this.Selection.Use && selectionflag_Numbering !== this.Selection.Flag ? this.Selection.EndPos : this.CurPos.ContentPos)
		this.private_CheckCurPage();
		return this.Content[nPos].RecalculateCurPos();
	}

	return {X : 0, Y : 0, Height : 0, PageNum : 0, Internal : {Line : 0, Page : 0, Range : 0}, Transform : null};
};
CDocument.prototype.controller_GetCurPage = function()
{
	var Pos = ( true === this.Selection.Use && selectionflag_Numbering !== this.Selection.Flag ? this.Selection.EndPos : this.CurPos.ContentPos );
	if (Pos >= 0 && ( null === this.FullRecalc.Id || this.FullRecalc.StartIndex > Pos ))
		return this.Content[Pos].Get_CurrentPage_Absolute();

	return -1;
};
CDocument.prototype.controller_AddNewParagraph = function(bRecalculate, bForceAdd)
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
		if (true !== bForceAdd && undefined != Item.Numbering_Get() && true === Item.IsEmpty({SkipNewLine : true}) && true === Item.IsCursorAtBegin())
		{
			Item.Numbering_Remove();
			Item.Set_Ind({FirstLine : undefined, Left : undefined, Right : Item.Pr.Ind.Right}, true);
		}
		else
		{
			var ItemReviewType = Item.Get_ReviewType();
			// Создаем новый параграф
			var NewParagraph   = new Paragraph(this.DrawingDocument, this);

			// Проверим позицию в текущем параграфе
			if (true === Item.IsCursorAtEnd())
			{
				var StyleId = Item.Style_Get();
				var NextId  = undefined;

				if (undefined != StyleId)
				{
					NextId = this.Styles.Get_Next(StyleId);

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
					if (NextId === this.Styles.Get_Default_Paragraph())
						NewParagraph.Style_Remove();
					else
						NewParagraph.Style_Add(NextId, true);
				}

				var SectPr = Item.Get_SectionPr();
				if (undefined !== SectPr)
				{
					Item.Set_SectionPr(undefined);
					NewParagraph.Set_SectionPr(SectPr);
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
			{
				Item.Split(NewParagraph);
			}

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
			var NewParagraph = new Paragraph(this.DrawingDocument, this);
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

	if (false !== bRecalculate)
	{
		this.Recalculate();

		this.Document_UpdateInterfaceState();
		//this.Document_UpdateRulersState()
		this.Document_UpdateSelectionState();
	}
};
CDocument.prototype.controller_AddInlineImage = function(W, H, Img, Chart, bFlow)
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
};
CDocument.prototype.controller_AddImages = function(aImages)
{
    if (true === this.Selection.Use)
        this.Remove(1, true);

    var Item = this.Content[this.CurPos.ContentPos];
    if (type_Paragraph === Item.GetType())
    {
        var Drawing, W, H;
        var ColumnSize = this.GetColumnSize();
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
};
CDocument.prototype.controller_AddOleObject = function(W, H, nWidthPix, nHeightPix, Img, Data, sApplicationId)
{
	if (true == this.Selection.Use)
		this.Remove(1, true);

	var Item = this.Content[this.CurPos.ContentPos];
	if (type_Paragraph == Item.GetType())
	{
		var Drawing   = new ParaDrawing(W, H, null, this.DrawingDocument, this, null);
		var Image = this.DrawingObjects.createOleObject(Data, sApplicationId, Img, 0, 0, W, H, nWidthPix, nHeightPix);
		Image.setParent(Drawing);
		Drawing.Set_GraphicObject(Image);
		this.AddToParagraph(Drawing);
		this.Select_DrawingObject(Drawing.Get_Id());
	}
	else
	{
		Item.AddOleObject(W, H, nWidthPix, nHeightPix, Img, Data, sApplicationId);
	}
};
CDocument.prototype.controller_AddTextArt = function(nStyle)
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
			this.SelectAll();
		}
	}
	else
	{
		Item.AddTextArt(nStyle);
	}
};
CDocument.prototype.controller_AddSignatureLine = function(oSignatureDrawing)
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
};
CDocument.prototype.controller_AddInlineTable = function(Cols, Rows)
{
	if (this.CurPos.ContentPos < 0)
		return false;

	// Сначала удаляем заселекченую часть
	if (true === this.Selection.Use)
	{
		this.Remove(1, true);
	}

	// Добавляем таблицу
	var Item = this.Content[this.CurPos.ContentPos];

	// Если мы внутри параграфа, тогда разрываем его и на месте разрыва добавляем таблицу.
	// А если мы внутри таблицы, тогда добавляем таблицу внутрь текущей таблицы.
	if (type_Paragraph === Item.GetType())
	{
		// Ширину таблицы делаем по минимальной ширине колонки.
		var Page   = this.Pages[this.CurPage];
		var SectPr = this.SectionsInfo.Get_SectPr(this.CurPos.ContentPos).SectPr;

		var PageFields = this.Get_PageFields(this.CurPage);

		// Создаем новую таблицу
		var W    = (PageFields.XLimit - PageFields.X + 2 * 1.9);
		var Grid = [];

		if (SectPr.Get_ColumnsCount() > 1)
		{
			for (var CurCol = 0, ColsCount = SectPr.Get_ColumnsCount(); CurCol < ColsCount; ++CurCol)
			{
				var ColumnWidth = SectPr.Get_ColumnWidth(CurCol);
				if (W > ColumnWidth)
					W = ColumnWidth;
			}

			W += 2 * 1.9;
		}

		W = Math.max(W, Cols * 2 * 1.9);

		for (var Index = 0; Index < Cols; Index++)
			Grid[Index] = W / Cols;

		var NewTable = new CTable(this.DrawingDocument, this, true, Rows, Cols, Grid);
		NewTable.Set_ParagraphPrOnAdd(Item);

		// Проверим позицию в текущем параграфе
		if (true === Item.IsCursorAtEnd() && undefined === Item.Get_SectionPr())
		{
			// Выставляем курсор в начало таблицы
			NewTable.MoveCursorToStartPos(false);
			this.Internal_Content_Add(this.CurPos.ContentPos + 1, NewTable);

			this.CurPos.ContentPos++;
		}
		else
		{
			// Создаем новый параграф
			var NewParagraph = new Paragraph(this.DrawingDocument, this);
			Item.Split(NewParagraph);

			// Добавляем новый параграф
			this.Internal_Content_Add(this.CurPos.ContentPos + 1, NewParagraph);

			// Выставляем курсор в начало таблицы
			NewTable.MoveCursorToStartPos(false);
			this.Internal_Content_Add(this.CurPos.ContentPos + 1, NewTable);

			this.CurPos.ContentPos++;
		}

	}
	else
	{
		Item.AddInlineTable(Cols, Rows);
	}

	this.Recalculate();
};
CDocument.prototype.controller_ClearParagraphFormatting = function()
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
				this.Content[Index].ClearParagraphFormatting();
			}
		}
	}
	else
	{
		this.Content[this.CurPos.ContentPos].ClearParagraphFormatting();
	}
};
CDocument.prototype.controller_AddToParagraph = function(ParaItem, bRecalculate)
{
	if (true === this.Selection.Use)
	{
		var bAddSpace = this.Is_WordSelection();

		var Type = ParaItem.Get_Type();
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
							this.Content[Index].Add(ParaItem.Copy());
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

				this.Document_UpdateSelectionState();
				this.Document_UpdateUndoRedoState();

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
				if (ParaItem.IsColumnBreak())
				{
					this.Content[this.CurPos.ContentPos].Add(ParaItem);
				}
				else
				{
					this.AddNewParagraph(undefined, true);
					var CurPos = this.CurPos.ContentPos - 1;
					this.Content[CurPos].MoveCursorToStartPos(false);
					this.Content[CurPos].AddToParagraph(ParaItem);
					this.Content[CurPos].Clear_Formatting();
				}
			}
			else
			{
				if (ParaItem.IsColumnBreak())
				{
					var oCurElement = this.Content[this.CurPos.ContentPos];
					var CurPos = this.CurPos.ContentPos;
					if (oCurElement && type_Paragraph === oCurElement.Get_Type() && oCurElement.IsColumnBreakOnLeft())
					{
						oCurElement.AddToParagraph(ParaItem);
					}
					else
					{
						this.AddNewParagraph(undefined, true);
						CurPos = this.CurPos.ContentPos;

						this.Content[CurPos].MoveCursorToStartPos(false);
						this.Content[CurPos].AddToParagraph(ParaItem);
					}
				}
				else
				{
					this.AddNewParagraph(undefined, true);
					this.AddNewParagraph(undefined, true);
					var CurPos = this.CurPos.ContentPos - 1;
					this.Content[CurPos].MoveCursorToStartPos(false);
					this.Content[CurPos].AddToParagraph(ParaItem);
					this.Content[CurPos].Clear_Formatting();
				}
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

		if (false != bRecalculate && type_Paragraph == Item.GetType())
		{
			if (para_TextPr === ParaItem.Type && false === ParaItem.Value.Check_NeedRecalc())
			{
				// Просто перерисовываем нужные страницы
				var StartPage = Item.Get_StartPage_Absolute();
				var EndPage   = StartPage + Item.Pages.length - 1;
				this.ReDraw(StartPage, EndPage);
			}
			else
			{
				// Нам нужно пересчитать все изменения, начиная с текущего элемента
				this.Recalculate(true);
			}

			if (false === this.TurnOffRecalcCurPos)
			{
				Item.RecalculateCurPos();
				Item.CurPos.RealX = Item.CurPos.X;
				Item.CurPos.RealY = Item.CurPos.Y;
			}
		}

		this.Document_UpdateSelectionState();
		this.Document_UpdateInterfaceState();
	}

	// Специальная заглушка для функции TextBox_Put
	if (true === this.Is_OnRecalculate())
		this.Document_UpdateUndoRedoState();
};
CDocument.prototype.controller_Remove = function(Count, bOnlyText, bRemoveOnlySelection, bOnTextAdd)
{
	// Делаем так, чтобы при выделении нумерации удалялась нумерация. А она удаляется по backspace.
	if (true === this.Selection.Use && selectionflag_Numbering == this.Selection.Flag && Count > 0)
		Count = -Count;

	this.private_Remove(Count, bOnlyText, bRemoveOnlySelection, bOnTextAdd);

	this.Recalculate();

	this.Document_UpdateInterfaceState();
	this.Document_UpdateRulersState();
};
CDocument.prototype.controller_GetCursorPosXY = function()
{
	if (true === this.Selection.Use)
	{
		if (selectionflag_Common === this.Selection.Flag)
			return this.Content[this.Selection.EndPos].GetCursorPosXY();

		return {X : 0, Y : 0};
	}
	else
	{
		return this.Content[this.CurPos.ContentPos].GetCursorPosXY();
	}
};
CDocument.prototype.controller_MoveCursorToStartPos = function(AddToSelect)
{
	if (true === AddToSelect)
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
CDocument.prototype.controller_MoveCursorToEndPos = function(AddToSelect)
{
	if (true === AddToSelect)
	{
		var StartPos = ( true === this.Selection.Use ? this.Selection.StartPos : this.CurPos.ContentPos );
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

		this.Content[StartPos].MoveCursorToEndPos(true, false);
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
};
CDocument.prototype.controller_MoveCursorLeft = function(AddToSelect, Word)
{
	if (this.CurPos.ContentPos < 0)
		return false;

	this.Remove_NumberingSelection();
	if (true === this.Selection.Use)
	{
		if (true === AddToSelect)
		{
			if (false === this.Content[this.Selection.EndPos].MoveCursorLeft(true, Word))
			{
				if (0 !== this.Selection.EndPos)
				{
					this.Selection.EndPos--;
					this.CurPos.ContentPos = this.Selection.EndPos;

					var Item = this.Content[this.Selection.EndPos];
					Item.MoveCursorLeftWithSelectionFromEnd(Word);
				}
			}

			// Проверяем не обнулился ли селект в последнем элементе. Такое могло быть, если была
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
			}
		}
	}
};
CDocument.prototype.controller_MoveCursorRight = function(AddToSelect, Word)
{
	if (this.CurPos.ContentPos < 0)
		return false;

	this.Remove_NumberingSelection();
	if (true === this.Selection.Use)
	{
		if (true === AddToSelect)
		{
			// Добавляем к селекту
			if (false === this.Content[this.Selection.EndPos].MoveCursorRight(true, Word))
			{
				// Нужно перейти в начало следующего элемента
				if (this.Content.length - 1 != this.Selection.EndPos)
				{
					this.Selection.EndPos++;
					this.CurPos.ContentPos = this.Selection.EndPos;

					var Item = this.Content[this.Selection.EndPos];
					Item.MoveCursorRightWithSelectionFromStart(Word);
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
			}
		}
	}
};
CDocument.prototype.controller_MoveCursorUp = function(AddToSelect)
{
	if (true === this.IsSelectionUse() && true !== AddToSelect)
		this.MoveCursorLeft(false, false);

	var bStopSelection = false;
	if (true !== this.IsSelectionUse() && true === AddToSelect)
	{
		bStopSelection = true;
		this.private_StartSelectionFromCurPos();
	}

	this.private_UpdateCursorXY(false, true);
	var Result = this.private_MoveCursorUp(this.CurPos.RealX, this.CurPos.RealY, AddToSelect);

	// TODO: Вообще Word селектит до начала данной колонки в таком случае, а не до начала документа
	if (true === AddToSelect && true !== Result)
		this.MoveCursorToStartPos(true);

	if (bStopSelection)
		this.private_StopSelection();
};
CDocument.prototype.controller_MoveCursorDown = function(AddToSelect)
{
	if (true === this.IsSelectionUse() && true !== AddToSelect)
		this.MoveCursorRight(false, false);

	var bStopSelection = false;
	if (true !== this.IsSelectionUse() && true === AddToSelect)
	{
		bStopSelection = true;
		this.private_StartSelectionFromCurPos();
	}

	this.private_UpdateCursorXY(false, true);
	var Result = this.private_MoveCursorDown(this.CurPos.RealX, this.CurPos.RealY, AddToSelect);

	if (true === AddToSelect && true !== Result)
		this.MoveCursorToEndPos(true);

	if (bStopSelection)
		this.private_StopSelection();
};
CDocument.prototype.controller_MoveCursorToEndOfLine = function(AddToSelect)
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

	this.Document_UpdateInterfaceState();
	this.private_UpdateCursorXY(true, true);
};
CDocument.prototype.controller_MoveCursorToStartOfLine = function(AddToSelect)
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
			if (this.Selection.StartPos == this.Selection.EndPos && false === this.Content[this.Selection.StartPos].Selection.Use)
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
			if (this.Selection.StartPos == this.Selection.EndPos && false === this.Content[this.Selection.StartPos].Selection.Use)
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

	this.Document_UpdateInterfaceState();
	this.private_UpdateCursorXY(true, true);
};
CDocument.prototype.controller_MoveCursorToXY = function(X, Y, PageAbs, AddToSelect)
{
	this.CurPage = PageAbs;

	this.Remove_NumberingSelection();
	if (true === this.Selection.Use)
	{
		if (true === AddToSelect)
		{
			this.Selection_SetEnd(X, Y, true);
		}
		else
		{
			this.RemoveSelection();

			var ContentPos         = this.Internal_GetContentPosByXY(X, Y);
			this.CurPos.ContentPos = ContentPos;
			var ElementPageIndex   = this.private_GetElementPageIndexByXY(ContentPos, X, Y, PageAbs);
			this.Content[ContentPos].MoveCursorToXY(X, Y, false, false, ElementPageIndex);

			this.Document_UpdateInterfaceState();
		}
	}
	else
	{
		if (true === AddToSelect)
		{
			this.StartSelectionFromCurPos();
			var oMouseEvent  = new AscCommon.CMouseEventHandler();
			oMouseEvent.Type = AscCommon.g_mouse_event_type_up;
			this.Selection_SetEnd(X, Y, oMouseEvent);
		}
		else
		{
			var ContentPos         = this.Internal_GetContentPosByXY(X, Y);
			this.CurPos.ContentPos = ContentPos;
			var ElementPageIndex   = this.private_GetElementPageIndexByXY(ContentPos, X, Y, PageAbs);
			this.Content[ContentPos].MoveCursorToXY(X, Y, false, false, ElementPageIndex);

			this.Document_UpdateInterfaceState();
		}
	}
};
CDocument.prototype.controller_MoveCursorToCell = function(bNext)
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
};
CDocument.prototype.controller_SetParagraphAlign = function(Align)
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
		var Item = this.Content[this.CurPos.ContentPos];
		Item.SetParagraphAlign(Align);
	}
};
CDocument.prototype.controller_SetParagraphSpacing = function(Spacing)
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
		var Item = this.Content[this.CurPos.ContentPos];
		Item.SetParagraphSpacing(Spacing);
	}
};
CDocument.prototype.controller_SetParagraphTabs = function(Tabs)
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
};
CDocument.prototype.controller_SetParagraphIndent = function(Ind)
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
};
CDocument.prototype.controller_SetParagraphNumbering = function(NumInfo)
{
	// TODO: Переделать применение нумерации (Обязательно объединить в общую функцию для классов CDocument, CDocumentContent)

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
				{
					this.Content[Index].Numbering_Remove();
				}
				else
				{
					this.Content[Index].SetParagraphNumbering(NumInfo);
				}
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

						if (undefined !== Prev && null !== Prev && type_Paragraph === Prev.GetType())
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
							else if ((type_Paragraph === this.Content[Index].GetType() && undefined === NumPr) || type_Paragraph !== this.Content[Index].GetType())
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
							// Если у нас выделен только 1 параграф, тогда посмотрим на следующий параграф, возможно у него есть нумерованный список.
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
							var NumPr = undefined;
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
	}
	else
	{
		var Item = this.Content[this.CurPos.ContentPos];
		if (type_Paragraph == Item.GetType())
		{
			if (NumInfo.SubType < 0)
			{
				// Убираем список у параграфа
				Item.Numbering_Remove();

				if (selectionflag_Numbering === this.Selection.Flag)
				{
					this.RemoveSelection();
					Item.Document_SetThisElementCurrent(true);
				}
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
									AbstractNum.Create_Default_Bullet();
							}
							else
							{
								// Если мы просто нажимаем добавить маркированный список, тогда мы пытаемся
								// присоединить его к списку предыдушего параграфа (если у предыдущего параграфа
								// есть список, и этот список маркированный)

								// Проверяем предыдущий элемент
								var Prev   = this.Content[this.CurPos.ContentPos - 1];
								var NumId  = undefined;
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
								if (undefined === NumId)
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
								var Prev   = this.Content[this.CurPos.ContentPos - 1];
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
						var NumPr       = Item.Numbering_Get();
						var AbstractNum = null;
						if (undefined != NumPr)
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
CDocument.prototype.controller_SetParagraphShd = function(Shd)
{
	if (this.CurPos.ContentPos < 0)
		return false;

	if (true === this.Selection.Use)
	{
		var StartPos = this.Selection.StartPos;
		var EndPos   = this.Selection.EndPos;

		if (true === this.UseTextShd && StartPos === EndPos && type_Paragraph === this.Content[StartPos].GetType() && false === this.Content[StartPos].Selection_CheckParaEnd() && selectionflag_Common === this.Selection.Flag)
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
};
CDocument.prototype.controller_SetParagraphStyle = function(Name)
{
	if (this.CurPos.ContentPos < 0)
		return false;

	if (true === this.Selection.Use)
	{
		if (selectionflag_Numbering === this.Selection.Flag)
			this.Remove_NumberingSelection();

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
			Item.SetParagraphStyle(Name);
		}
	}
	else
	{
		var Item = this.Content[this.CurPos.ContentPos];
		Item.SetParagraphStyle(Name);
	}
};
CDocument.prototype.controller_SetParagraphContextualSpacing = function(Value)
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
};
CDocument.prototype.controller_SetParagraphPageBreakBefore = function(Value)
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
			Item.SetParagraphPageBreakBefore(Value);
		}
	}
	else
	{
		var Item = this.Content[this.CurPos.ContentPos];
		Item.SetParagraphPageBreakBefore(Value);
	}
};
CDocument.prototype.controller_SetParagraphKeepLines = function(Value)
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
};
CDocument.prototype.controller_SetParagraphKeepNext = function(Value)
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
};
CDocument.prototype.controller_SetParagraphWidowControl = function(Value)
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
};
CDocument.prototype.controller_SetParagraphBorders = function(Borders)
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
		if (type_Paragraph == Item.GetType())
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
};
CDocument.prototype.controller_SetParagraphFramePr = function(FramePr, bDelete)
{
	if (true === this.Selection.Use)
	{
		if (this.Selection.StartPos === this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType())
		{
			this.Content[this.Selection.StartPos].SetParagraphFramePr(FramePr, bDelete);
			return;
		}

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
		{
			Element.SetParagraphFramePr(FramePr, bDelete);
			return;
		}

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
};
CDocument.prototype.controller_IncreaseDecreaseFontSize = function(bIncrease)
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
};
CDocument.prototype.controller_IncreaseDecreaseIndent = function(bIncrease)
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
};
CDocument.prototype.controller_SetImageProps = function(Props)
{
	if ((true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Table == this.Content[this.Selection.StartPos].GetType())
		|| (false == this.Selection.Use && type_Table == this.Content[this.CurPos.ContentPos].GetType()))
	{
		if (true == this.Selection.Use)
			this.Content[this.Selection.StartPos].SetImageProps(Props);
		else
			this.Content[this.CurPos.ContentPos].SetImageProps(Props);
	}
};
CDocument.prototype.controller_SetTableProps = function(Props)
{
	var Pos = -1;
	if (true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos)
		Pos = this.Selection.StartPos;
	else if (false === this.Selection.Use)
		Pos = this.CurPos.ContentPos;

	if (-1 !== Pos)
		this.Content[Pos].SetTableProps(Props);
};
CDocument.prototype.controller_GetCalculatedParaPr = function()
{
	var Result_ParaPr = new CParaPr();
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
			var Item   = this.Content[Index];
			var TempPr = Item.GetCalculatedParaPr();
			Pr         = Pr.Compare(TempPr);
		}

		if (undefined === Pr.Ind.Left)
			Pr.Ind.Left = StartPr.Ind.Left;

		if (undefined === Pr.Ind.Right)
			Pr.Ind.Right = StartPr.Ind.Right;

		if (undefined === Pr.Ind.FirstLine)
			Pr.Ind.FirstLine = StartPr.Ind.FirstLine;

		Result_ParaPr             = Pr;
		Result_ParaPr.CanAddTable = ( true === Pr.Locked ? false : true );

		// Если мы находимся в рамке, тогда дополняем ее свойства настройками границы и настройкой текста (если это буквица)
		if (undefined != Result_ParaPr.FramePr && type_Paragraph === this.Content[StartPos].GetType())
		{
			this.Content[StartPos].Supplement_FramePr(Result_ParaPr.FramePr);
		}
		else if (StartPos === EndPos && StartPos > 0 && type_Paragraph === this.Content[StartPos - 1].GetType())
		{
			var PrevFrame = this.Content[StartPos - 1].Get_FramePr();
			if (undefined != PrevFrame && undefined != PrevFrame.DropCap)
			{
				Result_ParaPr.FramePr = PrevFrame.Copy();
				this.Content[StartPos - 1].Supplement_FramePr(Result_ParaPr.FramePr);
			}
		}

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
			Result_ParaPr.CanAddTable = ( ( true === Locked ) ? ( ( true === Item.IsCursorAtEnd() ) ? true : false ) : true );

			// Если мы находимся в рамке, тогда дополняем ее свойства настройками границы и настройкой текста (если это буквица)
			if (undefined != Result_ParaPr.FramePr)
			{
				Item.Supplement_FramePr(Result_ParaPr.FramePr);
			}
			else if (this.CurPos.ContentPos > 0 && type_Paragraph === this.Content[this.CurPos.ContentPos - 1].GetType())
			{
				var PrevFrame = this.Content[this.CurPos.ContentPos - 1].Get_FramePr();
				if (undefined != PrevFrame && undefined != PrevFrame.DropCap)
				{
					Result_ParaPr.FramePr = PrevFrame.Copy();
					this.Content[this.CurPos.ContentPos - 1].Supplement_FramePr(Result_ParaPr.FramePr);
				}
			}
		}
		else
		{
			Result_ParaPr = Item.GetCalculatedParaPr();
		}
	}

	if (Result_ParaPr.Shd && Result_ParaPr.Shd.Unifill)
	{
		Result_ParaPr.Shd.Unifill.check(this.theme, this.Get_ColorMap());
	}

	return Result_ParaPr;
};
CDocument.prototype.controller_GetCalculatedTextPr = function()
{
	var Result_TextPr = null;
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
};
CDocument.prototype.controller_GetDirectParaPr = function()
{
	var Result_ParaPr = null;

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

	return Result_ParaPr;
};
CDocument.prototype.controller_GetDirectTextPr = function()
{
	var Result_TextPr = null;

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
};
CDocument.prototype.controller_RemoveSelection = function(bNoCheckDrawing)
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

				this.Selection.Use   = false;
				this.Selection.Start = false;

				this.Selection.StartPos = 0;
				this.Selection.EndPos   = 0;

				// Убираем селект и возвращаем курсор
				this.DrawingDocument.SelectEnabled(false);
				this.DrawingDocument.TargetStart();
				this.DrawingDocument.TargetShow();

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

				this.Selection.Use   = false;
				this.Selection.Start = false;
				this.Selection.Flag  = selectionflag_Common;

				// Убираем селект и возвращаем курсор
				this.DrawingDocument.SelectEnabled(false);
				this.DrawingDocument.TargetStart();
				this.DrawingDocument.TargetShow();

				break;
			}
		}
	}
};
CDocument.prototype.controller_IsSelectionEmpty = function(bCheckHidden)
{
	if (true === this.Selection.Use)
	{
		if (selectionflag_Numbering == this.Selection.Flag)
			return false;
		else if (true === this.IsMovingTableBorder())
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
};
CDocument.prototype.controller_DrawSelectionOnPage = function(PageAbs)
{
	if (true !== this.Selection.Use)
		return;

	var Page = this.Pages[PageAbs];
	for (var SectionIndex = 0, SectionsCount = Page.Sections.length; SectionIndex < SectionsCount; ++SectionIndex)
	{
		var PageSection = Page.Sections[SectionIndex];
		for (var ColumnIndex = 0, ColumnsCount = PageSection.Columns.length; ColumnIndex < ColumnsCount; ++ColumnIndex)
		{
			var Pos_start = this.Pages[PageAbs].Pos;
			var Pos_end   = this.Pages[PageAbs].EndPos;

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

					for (var Index = Start; Index <= End; ++Index)
					{
						var ElementPage = this.private_GetElementPageIndex(Index, PageAbs, ColumnIndex, ColumnsCount);
						this.Content[Index].DrawSelectionOnPage(ElementPage);
					}

					if (PageAbs >= 2 && End < this.Pages[PageAbs - 2].EndPos)
					{
						this.Selection.UpdateOnRecalc = false;
						this.DrawingDocument.OnSelectEnd();
					}

					break;
				}
				case selectionflag_Numbering:
				{
					if (null == this.Selection.Data)
						break;

					var Count = this.Selection.Data.length;
					for (var Index = 0; Index < Count; ++Index)
					{
						var ElementPos = this.Selection.Data[Index];
						if (Pos_start <= ElementPos && ElementPos <= Pos_end)
						{
							var ElementPage = this.private_GetElementPageIndex(ElementPos, PageAbs, ColumnIndex, ColumnsCount);
							this.Content[ElementPos].DrawSelectionOnPage(ElementPage);
						}
					}

					if (PageAbs >= 2 && this.Selection.Data[this.Selection.Data.length - 1] < this.Pages[PageAbs - 2].EndPos)
					{
						this.Selection.UpdateOnRecalc = false;
						this.DrawingDocument.OnSelectEnd();
					}

					break;
				}
			}
		}
	}
};
CDocument.prototype.controller_GetSelectionBounds = function()
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
CDocument.prototype.controller_IsMovingTableBorder = function()
{
	if (null != this.Selection.Data && true === this.Selection.Data.TableBorder)
		return true;

	return false;
};
CDocument.prototype.controller_CheckPosInSelection = function(X, Y, PageAbs, NearPos)
{
	if (true === this.Footnotes.CheckHitInFootnote(X, Y, PageAbs))
		return false;

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

				if (undefined !== NearPos)
				{
					for (var Index = Start; Index <= End; Index++)
					{
						if (true === this.Content[Index].CheckPosInSelection(0, 0, 0, NearPos))
							return true;
					}

					return false;
				}
				else
				{
					var ContentPos = this.Internal_GetContentPosByXY(X, Y, PageAbs, NearPos);
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
						var ElementPageIndex = this.private_GetElementPageIndexByXY(ContentPos, X, Y, PageAbs);
						return this.Content[ContentPos].CheckPosInSelection(X, Y, ElementPageIndex, undefined);
					}
				}
			}
			case selectionflag_Numbering:
			{
				return false;
			}
		}

		return false;
	}

	return false;
};
CDocument.prototype.controller_SelectAll = function()
{
	if (true === this.Selection.Use)
		this.RemoveSelection();

	this.DrawingDocument.SelectEnabled(true);
	this.DrawingDocument.TargetEnd();

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
};
CDocument.prototype.controller_GetSelectedContent = function(SelectedContent)
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
};
CDocument.prototype.controller_UpdateCursorType = function(X, Y, PageAbs, MouseEvent)
{
	var bInText      = (null === this.IsInText(X, Y, PageAbs) ? false : true);
	var bTableBorder = (null === this.IsTableBorder(X, Y, PageAbs) ? false : true);

	// Ничего не делаем
	if (true === this.DrawingObjects.updateCursorType(PageAbs, X, Y, MouseEvent, ( true === bInText || true === bTableBorder ? true : false )))
		return;

	var ContentPos       = this.Internal_GetContentPosByXY(X, Y, PageAbs);
	var Item             = this.Content[ContentPos];
	var ElementPageIndex = this.private_GetElementPageIndexByXY(ContentPos, X, Y, PageAbs);
	Item.UpdateCursorType(X, Y, ElementPageIndex);
};
CDocument.prototype.controller_PasteFormatting = function(TextPr, ParaPr)
{
	if (true === this.Selection.Use)
	{
		if (selectionflag_Common === this.Selection.Flag)
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
				this.Content[Pos].PasteFormatting(TextPr, ParaPr, Start === End ? false : true);
			}
		}
	}
	else
	{
		this.Content[this.CurPos.ContentPos].PasteFormatting(TextPr, ParaPr, true);
	}
};
CDocument.prototype.controller_IsSelectionUse = function()
{
	if (true === this.Selection.Use)
		return true;

	return false;
};
CDocument.prototype.controller_IsTextSelectionUse = function()
{
	return this.Selection.Use;
};
CDocument.prototype.controller_GetCurPosXY = function()
{
	if (true === this.Selection.Use)
	{
		if (selectionflag_Numbering === this.Selection.Flag)
			return {X : 0, Y : 0};
		else
			return this.Content[this.Selection.EndPos].GetCurPosXY();
	}
	else
	{
		return this.Content[this.CurPos.ContentPos].GetCurPosXY();
	}
};
CDocument.prototype.controller_GetSelectedText = function(bClearText, oPr)
{
	if ((true === this.Selection.Use && selectionflag_Common === this.Selection.Flag) || false === this.Selection.Use)
	{
		if (true === bClearText && this.Selection.StartPos === this.Selection.EndPos)
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

	return null;
};
CDocument.prototype.controller_GetCurrentParagraph = function(bIgnoreSelection, arrSelectedParagraphs)
{
	if (null !== arrSelectedParagraphs && true === this.Selection.Use)
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
};
CDocument.prototype.controller_GetSelectedElementsInfo = function(Info)
{
	if (true === this.Selection.Use)
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
			if (this.Selection.StartPos != this.Selection.EndPos)
				Info.Set_MixedSelection();
			else
				this.Content[this.Selection.StartPos].GetSelectedElementsInfo(Info);
		}
	}
	else
	{
		this.Content[this.CurPos.ContentPos].GetSelectedElementsInfo(Info);
	}
};
CDocument.prototype.controller_AddTableRow = function(bBefore)
{
	if ((true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType())
		|| (false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType()))
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
	}
};
CDocument.prototype.controller_AddTableColumn = function(bBefore)
{
	if ((true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType())
		|| (false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType()))
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
	}
};
CDocument.prototype.controller_RemoveTableRow = function()
{
	if ((true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType())
		|| (false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType()))
	{
		var Pos = 0;
		if (true === this.Selection.Use)
			Pos = this.Selection.StartPos;
		else
			Pos = this.CurPos.ContentPos;

		if (false === this.Content[Pos].RemoveTableRow())
			this.controller_RemoveTable();
	}
};
CDocument.prototype.controller_RemoveTableColumn = function()
{
	if ((true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType())
		|| (false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType()))
	{
		var Pos = 0;
		if (true === this.Selection.Use)
			Pos = this.Selection.StartPos;
		else
			Pos = this.CurPos.ContentPos;

		if (false === this.Content[Pos].RemoveTableColumn())
			this.controller_RemoveTable();
	}
};
CDocument.prototype.controller_MergeTableCells = function()
{
	if ((true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType())
		|| (false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType()))
	{
		var Pos = 0;
		if (true === this.Selection.Use)
			Pos = this.Selection.StartPos;
		else
			Pos = this.CurPos.ContentPos;

		this.Content[Pos].MergeTableCells();
	}
};
CDocument.prototype.controller_SplitTableCells = function(Cols, Rows)
{
	if ((true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType())
		|| (false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType()))
	{
		var Pos = 0;
		if (true === this.Selection.Use)
			Pos = this.Selection.StartPos;
		else
			Pos = this.CurPos.ContentPos;

		this.Content[Pos].SplitTableCells(Rows, Cols);
	}
};
CDocument.prototype.controller_RemoveTable = function()
{
	if ((true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType())
		|| (false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType()))
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
		}
		else
		{
			Table.RemoveTable();
		}
	}
};
CDocument.prototype.controller_SelectTable = function(Type)
{
	if ((true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType())
		|| (false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType()))
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
	}
};
CDocument.prototype.controller_CanMergeTableCells = function()
{
	if ((true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType())
		|| (false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType()))
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
CDocument.prototype.controller_CanSplitTableCells = function()
{
	if ((true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType())
		|| (false == this.Selection.Use && type_Paragraph !== this.Content[this.CurPos.ContentPos].GetType()))
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
CDocument.prototype.controller_UpdateInterfaceState = function()
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
		if (docpostype_Content == this.CurPos.Type && ( ( true === this.Selection.Use && this.Selection.StartPos == this.Selection.EndPos && type_Paragraph == this.Content[this.Selection.StartPos].GetType() ) || ( false == this.Selection.Use && type_Paragraph == this.Content[this.CurPos.ContentPos].GetType() ) ))
		{
			if (true == this.Selection.Use)
				this.Content[this.Selection.StartPos].Document_UpdateInterfaceState();
			else
				this.Content[this.CurPos.ContentPos].Document_UpdateInterfaceState();
		}
	}
};
CDocument.prototype.controller_UpdateRulersState = function()
{
	this.Document_UpdateRulersStateBySection();

	if (true === this.Selection.Use)
	{
		if (this.Selection.StartPos == this.Selection.EndPos && type_Paragraph !== this.Content[this.Selection.StartPos].GetType())
		{
			var PagePos = this.Get_DocumentPagePositionByContentPosition(this.GetContentPosition(true, true));

			var Page   = PagePos ? PagePos.Page : this.CurPage;
			var Column = PagePos ? PagePos.Column : 0;

			var ElementPos       = this.Selection.StartPos;
			var Element          = this.Content[ElementPos];
			var ElementPageIndex = this.private_GetElementPageIndex(ElementPos, Page, Column, Element.Get_ColumnsCount());
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
		this.private_CheckCurPage();

		if (this.CurPos.ContentPos >= 0 && (null === this.FullRecalc.Id || this.FullRecalc.StartIndex > this.CurPos.ContentPos))
		{
			var PagePos = this.Get_DocumentPagePositionByContentPosition(this.GetContentPosition(false));

			var Page   = PagePos ? PagePos.Page : this.CurPage;
			var Column = PagePos ? PagePos.Column : 0;

			var ElementPos       = this.CurPos.ContentPos;
			var Element          = this.Content[ElementPos];
			var ElementPageIndex = this.private_GetElementPageIndex(ElementPos, Page, Column, Element.Get_ColumnsCount());
			Element.Document_UpdateRulersState(ElementPageIndex);
		}
	}
};
CDocument.prototype.controller_UpdateSelectionState = function()
{
	if (true === this.Selection.Use)
	{
		// Выделение нумерации
		if (selectionflag_Numbering == this.Selection.Flag)
		{
			this.DrawingDocument.TargetEnd();
			this.DrawingDocument.SelectEnabled(true);
			this.DrawingDocument.SelectShow();
		}
		// Обрабатываем движение границы у таблиц
		else if (true === this.IsMovingTableBorder())
		{
			// Убираем курсор, если он был
			this.DrawingDocument.TargetEnd();
			this.DrawingDocument.SetCurrentPage(this.CurPage);
		}
		else
		{
			if (false === this.IsSelectionEmpty())
			{
				if (true !== this.Selection.Start)
				{
					this.private_CheckCurPage();
					this.RecalculateCurPos();
				}
				this.private_UpdateTracks(true, false);

				this.DrawingDocument.TargetEnd();
				this.DrawingDocument.SelectEnabled(true);
				this.DrawingDocument.SelectShow();
			}
			else
			{
				if (true !== this.Selection.Start)
				{
					this.RemoveSelection();
				}

				this.private_CheckCurPage();
				this.RecalculateCurPos();
				this.private_UpdateTracks(true, true);

				this.DrawingDocument.SelectEnabled(false);
				this.DrawingDocument.TargetStart();
				this.DrawingDocument.TargetShow();
			}
		}
	}
	else
	{
		this.RemoveSelection();
		this.private_CheckCurPage();
		this.RecalculateCurPos();
		this.private_UpdateTracks(false, false);

		this.DrawingDocument.SelectEnabled(false);
		this.DrawingDocument.TargetShow();
	}
};
CDocument.prototype.controller_GetSelectionState = function()
{
	var State;
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
	{
		State = this.Content[this.CurPos.ContentPos].GetSelectionState();
	}

	return State;
};
CDocument.prototype.controller_SetSelectionState = function(State, StateIndex)
{
	if (true === this.Selection.Use)
	{
		// Выделение нумерации
		if (selectionflag_Numbering == this.Selection.Flag)
		{
			if (type_Paragraph === this.Content[this.Selection.StartPos].Get_Type())
			{
				var NumPr = this.Content[this.Selection.StartPos].Numbering_Get();
				if (undefined !== NumPr)
					this.Document_SelectNumbering(NumPr, this.Selection.StartPos);
				else
					this.RemoveSelection();
			}
			else
				this.RemoveSelection();
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

			var CurState = State[StateIndex];
			for (var Index = StartPos; Index <= EndPos; Index++)
			{
				this.Content[Index].SetSelectionState(CurState[Index - StartPos], CurState[Index - StartPos].length - 1);
			}
		}
	}
	else
	{
		this.Content[this.CurPos.ContentPos].SetSelectionState(State, StateIndex);
	}
};
CDocument.prototype.controller_AddHyperlink = function(Props)
{
	if (false === this.Selection.Use || this.Selection.StartPos === this.Selection.EndPos)
	{
		var Pos = ( true == this.Selection.Use ? this.Selection.StartPos : this.CurPos.ContentPos );
		this.Content[Pos].AddHyperlink(Props);
	}
};
CDocument.prototype.controller_ModifyHyperlink = function(Props)
{
	if (false == this.Selection.Use || this.Selection.StartPos == this.Selection.EndPos)
	{
		var Pos = ( true == this.Selection.Use ? this.Selection.StartPos : this.CurPos.ContentPos );
		this.Content[Pos].ModifyHyperlink(Props);
	}
};
CDocument.prototype.controller_RemoveHyperlink = function()
{
	if (false == this.Selection.Use || this.Selection.StartPos == this.Selection.EndPos)
	{
		var Pos = ( true == this.Selection.Use ? this.Selection.StartPos : this.CurPos.ContentPos );
		this.Content[Pos].RemoveHyperlink();
	}
};
CDocument.prototype.controller_CanAddHyperlink = function(bCheckInHyperlink)
{
	if (true === this.Selection.Use)
	{
		if (selectionflag_Common === this.Selection.Flag)
		{
			if (this.Selection.StartPos != this.Selection.EndPos)
				return false;

			return this.Content[this.Selection.StartPos].CanAddHyperlink(bCheckInHyperlink);
		}
	}
	else
	{
		return this.Content[this.CurPos.ContentPos].CanAddHyperlink(bCheckInHyperlink);
	}

	return false;
};
CDocument.prototype.controller_IsCursorInHyperlink = function(bCheckEnd)
{
	if (true === this.Selection.Use)
	{
		if (selectionflag_Common === this.Selection.Flag)
		{
			if (this.Selection.StartPos != this.Selection.EndPos)
				return null;

			return this.Content[this.Selection.StartPos].IsCursorInHyperlink(bCheckEnd);
		}
	}
	else
	{
		return this.Content[this.CurPos.ContentPos].IsCursorInHyperlink(bCheckEnd);
	}

	return null;
};
CDocument.prototype.controller_AddComment = function(Comment)
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
		{
			this.Content[StartPos].AddComment(Comment, true, true);
		}
		else
		{
			this.Content[StartPos].AddComment(Comment, true, false);
			this.Content[EndPos].AddComment(Comment, false, true);
		}
	}
	else
	{
		this.Content[this.CurPos.ContentPos].AddComment(Comment, true, true);
	}
};
CDocument.prototype.controller_CanAddComment = function()
{
	if (selectionflag_Common === this.Selection.Flag)
	{
		if (true === this.Selection.Use && this.Selection.StartPos != this.Selection.EndPos)
		{
			return true;
		}
		else
		{
			var Pos     = ( this.Selection.Use === true ? this.Selection.StartPos : this.CurPos.ContentPos );
			var Element = this.Content[Pos];
			return Element.CanAddComment();
		}
	}

	return false;
};
CDocument.prototype.controller_GetSelectionAnchorPos = function()
{
	var Pos = ( true === this.Selection.Use ? ( this.Selection.StartPos < this.Selection.EndPos ? this.Selection.StartPos : this.Selection.EndPos ) : this.CurPos.ContentPos );
	return this.Content[Pos].GetSelectionAnchorPos();
};
CDocument.prototype.controller_StartSelectionFromCurPos = function()
{
	this.Selection.StartPos = this.CurPos.ContentPos;
	this.Selection.EndPos   = this.CurPos.ContentPos;
	this.Content[this.CurPos.ContentPos].StartSelectionFromCurPos();
};
CDocument.prototype.controller_SaveDocumentStateBeforeLoadChanges = function(State)
{
	State.Pos      = this.GetContentPosition(false, false);
	State.StartPos = this.GetContentPosition(true, true);
	State.EndPos   = this.GetContentPosition(true, false);
};
CDocument.prototype.controller_RestoreDocumentStateAfterLoadChanges = function(State)
{
	if (true === this.Selection.Use)
	{
		this.SetContentPosition(State.StartPos, 0, 0);
		this.SetContentSelection(State.StartPos, State.EndPos, 0, 0, 0);
	}
	else
	{
		this.SetContentPosition(State.Pos, 0, 0);
		this.NeedUpdateTarget = true;
	}
};
CDocument.prototype.controller_GetColumnSize = function()
{
	var ContentPos = true === this.Selection.Use ? ( this.Selection.StartPos < this.Selection.EndPos ? this.Selection.StartPos : this.Selection.EndPos ) : this.CurPos.ContentPos;

	var PagePos   = this.Get_DocumentPagePositionByContentPosition(this.GetContentPosition(this.Selection.Use, false));
	var ColumnAbs = PagePos ? PagePos.Column : 0;

	var SectPr = this.Get_SectPr(ContentPos);
	var Y      = SectPr.Get_PageMargin_Top();
	var YLimit = SectPr.Get_PageHeight() - SectPr.Get_PageMargin_Bottom();
	var X      = SectPr.Get_PageMargin_Left();
	var XLimit = SectPr.Get_PageWidth() - SectPr.Get_PageMargin_Right();

	var ColumnsCount = SectPr.Get_ColumnsCount();
	for (var ColumnIndex = 0; ColumnIndex < ColumnAbs; ++ColumnIndex)
	{
		X += SectPr.Get_ColumnWidth(ColumnIndex);
		X += SectPr.Get_ColumnSpace(ColumnIndex);
	}

	if (ColumnsCount - 1 !== ColumnAbs)
		XLimit = X + SectPr.Get_ColumnWidth(ColumnAbs);

	return {
		W : XLimit - X,
		H : YLimit - Y
	};
};
CDocument.prototype.controller_GetCurrentSectionPr = function()
{
	var nContentPos = this.CurPos.ContentPos;
	return this.SectionsInfo.Get_SectPr(nContentPos).SectPr;
};
CDocument.prototype.controller_AddContentControl = function(nContentControlType)
{
	return this.private_AddContentControl(nContentControlType);
};
//----------------------------------------------------------------------------------------------------------------------
//
//----------------------------------------------------------------------------------------------------------------------
CDocument.prototype.RemoveTextSelection = function()
{
	this.Controller.RemoveTextSelection();
};
CDocument.prototype.AddFormTextField = function(sName, sDefaultText)
{
	if (false === this.Document_Is_SelectionLocked(AscCommon.changestype_Paragraph_Content))
	{
		this.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddMailMergeField);

		var oField = new ParaField(fieldtype_FORMTEXT);
		var oRun = new ParaRun();
		oField.SetFormFieldName(sName);
		oField.SetFormFieldDefaultText(sDefaultText);
		for (var nIndex = 0, nLen = sDefaultText.length; nIndex < nLen; ++nIndex)
		{
			oRun.Add_ToContent(nIndex, new ParaText(sDefaultText.charAt(nIndex)));
		}
		oField.Add_ToContent(0, oRun);

		this.Register_Field(oField);
		this.AddToParagraph(oField);
		this.Document_UpdateInterfaceState();
	}
};
CDocument.prototype.GetAllFormTextFields = function()
{
	return this.FieldsManager.GetAllFieldsByType(fieldtype_FORMTEXT);
};
CDocument.prototype.IsFillingFormMode = function()
{
	return (this.Api.restrictions === Asc.c_oAscRestrictionType.OnlyForms);
};
CDocument.prototype.IsInFormField = function()
{
	var oSelectedInfo = this.GetSelectedElementsInfo();
	var oField        = oSelectedInfo.Get_Field();
	var oInlineSdt    = oSelectedInfo.GetInlineLevelSdt();
	var oBlockSdt     = oSelectedInfo.GetBlockLevelSdt();

	return (oBlockSdt || oInlineSdt || (oField && fieldtype_FORMTEXT === oField.Get_FieldType())) ? true : false;
};
CDocument.prototype.IsFormFieldEditing = function()
{
	if (true === this.IsFillingFormMode() && true === this.IsInFormField())
		return true;

	return false;
};
CDocument.prototype.MoveToFillingForm = function(isNext)
{
	var oRes = this.FindNextFillingForm(isNext, true, true);

	if (!oRes)
		oRes = this.FindNextFillingForm(isNext, true, false);

	if (oRes)
	{
		this.RemoveSelection();

		if (oRes instanceof CBlockLevelSdt || oRes instanceof CInlineLevelSdt)
		{
			oRes.SelectContentControl();
		}
		else if (oRes instanceof ParaField)
		{
			oRes.SelectThisElement();
		}
	}
};
CDocument.prototype.SelectContentControl = function(Id)
{
	var oBlockLevelSdt = this.TableId.Get_ById(Id);
	if (oBlockLevelSdt)
	{
		this.RemoveSelection();
		oBlockLevelSdt.SelectContentControl();

		this.Document_UpdateInterfaceState();
		this.Document_UpdateRulersState();
		this.Document_UpdateSelectionState();
	}
};
CDocument.prototype.OnContentControlTrackEnd = function(Id, NearestPos, isCopy)
{
	return this.On_DragTextEnd(NearestPos, isCopy);
};
CDocument.prototype.AddContentControl = function(nContentControlType)
{
	return this.Controller.AddContentControl(nContentControlType);
};
CDocument.prototype.GetAllContentControls = function()
{
	var arrContentControls = [];

	this.SectionsInfo.GetAllContentControls(arrContentControls);

	for (var nIndex = 0, nCount = this.Content.length; nIndex < nCount; ++nIndex)
	{
		this.Content[nIndex].GetAllContentControls(arrContentControls);
	}
	return arrContentControls;
};
CDocument.prototype.RemoveContentControl = function(Id)
{
	var oContentControl = this.TableId.Get_ById(Id);
	if (!oContentControl)
		return;

	if (AscCommonWord.sdttype_BlockLevel === oContentControl.GetContentControlType() && oContentControl.Parent)
	{
		this.RemoveSelection();
		var oDocContent = oContentControl.Parent;
		oDocContent.Update_ContentIndexing();
		var nIndex = oContentControl.GetIndex();

		var nCurPos = oDocContent.CurPos.ContentPos;
		oDocContent.Remove_FromContent(nIndex, 1);

		if (nIndex === nCurPos)
		{
			if (nIndex >= oDocContent.Get_ElementsCount())
			{
				oDocContent.MoveCursorToEndPos();
			}
			else
			{
				oDocContent.CurPos.ContentPos = Math.max(0, Math.min(oDocContent.Get_ElementsCount() - 1, nIndex));;
				oDocContent.Content[oDocContent.CurPos.ContentPos].MoveCursorToStartPos();
			}
		}
		else if (nIndex < nCurPos)
		{
			oDocContent.CurPos.ContentPos = Math.max(0, Math.min(oDocContent.Get_ElementsCount() - 1, nCurPos - 1));
		}
	}
	else if (AscCommonWord.sdttype_InlineLevel === oContentControl.GetContentControlType())
	{
		this.SelectContentControl(Id);
		this.RemoveBeforePaste();
	}
};
CDocument.prototype.RemoveContentControlWrapper = function(Id)
{
	var oContentControl = this.TableId.Get_ById(Id);
	if (!oContentControl)
		return;

	this.History.Create_NewPoint();

	oContentControl.RemoveContentControlWrapper();
	this.Recalculate();
	this.Document_UpdateInterfaceState();
	this.Document_UpdateSelectionState();
};
CDocument.prototype.GetContentControl = function(Id)
{
	return this.TableId.Get_ById(Id);
};
CDocument.prototype.ClearContentControl = function(Id)
{
	var oContentControl = this.TableId.Get_ById(Id);
	if (!oContentControl)
		return null;

	this.RemoveSelection();

	if (oContentControl.GetContentControlType
		&& (AscCommonWord.sdttype_BlockLevel === oContentControl.GetContentControlType()
		|| AscCommonWord.sdttype_InlineLevel === oContentControl.GetContentControlType()))
	{
		oContentControl.ClearContentControl();
		oContentControl.SetThisElementCurrent();
		oContentControl.MoveCursorToStartPos();
	}

	return oContentControl;
};
CDocument.prototype.GetAllSignatures = function()
{
    return this.DrawingObjects.getAllSignatures();
};
CDocument.prototype.SetCheckContentControlsLock = function(isLocked)
{
	this.CheckContentControlsLock = isLocked;
};
CDocument.prototype.IsCheckContentControlsLock = function()
{
	return this.CheckContentControlsLock;
};
CDocument.prototype.IsEditCommentsMode = function()
{
	return (this.Api.restrictions === Asc.c_oAscRestrictionType.OnlyComments);
};
CDocument.prototype.IsViewMode = function()
{
	return this.Api.isViewMode;
};
CDocument.prototype.CanEdit = function()
{
	if (this.IsViewMode() || this.IsEditCommentsMode() || this.IsFillingFormMode())
		return false;

	return true;
};
CDocument.prototype.private_CheckCursorPosInFillingFormMode = function()
{
	if (this.IsFillingFormMode() && !this.IsInFormField())
	{
		this.MoveToFillingForm(true);
		this.Document_UpdateSelectionState();
		this.Document_UpdateInterfaceState();
	}
};
CDocument.prototype.OnEndLoadScript = function()
{
	this.Update_SectionsInfo();
	this.Check_SectionLastParagraph();
	this.Styles.Check_StyleNumberingOnLoad(this.Numbering);

	var arrParagraphs = this.GetAllParagraphs({All : true});
	for (var nIndex = 0, nCount = arrParagraphs.length; nIndex < nCount; ++nIndex)
	{
		arrParagraphs[nIndex].Recalc_CompiledPr();
		arrParagraphs[nIndex].Recalc_RunsCompiledPr();
	}
};
CDocument.prototype.BeginViewModeInReview = function(isResult)
{
	if (0 !== this.ViewModeInReview.mode)
		this.EndViewModeInReview();

	this.ViewModeInReview.mode = isResult ? 1 : -1;

	this.ViewModeInReview.isFastCollaboration = this.CollaborativeEditing.Is_Fast();
	this.CollaborativeEditing.Set_Fast(false);

	this.History.SaveRedoPoints();
	if (isResult)
		this.Accept_AllRevisionChanges(true);
	else
		this.Reject_AllRevisionChanges(true);

	this.CollaborativeEditing.Set_GlobalLock(true);
};
CDocument.prototype.EndViewModeInReview = function()
{
	if (0 === this.ViewModeInReview.mode)
		return;

	this.ViewModeInReview.mode = 0;

	this.CollaborativeEditing.Set_GlobalLock(false);

	this.Document_Undo();
	this.History.Clear_Redo();
	this.History.PopRedoPoints();

	if (this.ViewModeInReview.isFastCollaboration)
		this.CollaborativeEditing.Set_Fast(true);
};
CDocument.prototype.StartCollaborationEditing = function()
{
	this.CollaborativeEditing.Start_CollaborationEditing();
	this.DrawingDocument.Start_CollaborationEditing();
	this.EndViewModeInReview();
};
CDocument.prototype.EndCollaborationEditing = function()
{
	this.CollaborativeEditing.End_CollaborationEditing();
};
CDocument.prototype.IsViewModeInReview = function()
{
	return 0 !== this.ViewModeInReview.mode ? true : false;
};
CDocument.prototype.AddField = function(nType, oPr)
{
	if (fieldtype_PAGENUM === nType)
	{
		var oParagraph = this.GetCurrentParagraph();
		if (!oParagraph)
			return false;

		var nIndex = -1;
		var oRun = new ParaRun();
		oRun.Add_ToContent(++nIndex, new ParaFieldChar(fldchartype_Begin, this));
		oRun.Add_ToContent(++nIndex, new ParaInstrText("P"));
		oRun.Add_ToContent(++nIndex, new ParaInstrText("A"));
		oRun.Add_ToContent(++nIndex, new ParaInstrText("G"));
		oRun.Add_ToContent(++nIndex, new ParaInstrText("E"));
		oRun.Add_ToContent(++nIndex, new ParaFieldChar(fldchartype_Separate, this));
		oRun.Add_ToContent(++nIndex, new ParaText("1"));
		oRun.Add_ToContent(++nIndex, new ParaFieldChar(fldchartype_End, this));
		oParagraph.Add(oRun);
		return true;
	}
	else if (fieldtype_TOC === nType)
	{
		var oParagraph = this.GetCurrentParagraph();
		if (!oParagraph)
			return false;

		var nIndex = -1;
		var oRun = new ParaRun();
		oRun.Add_ToContent(++nIndex, new ParaFieldChar(fldchartype_Begin, this));
		oRun.Add_ToContent(++nIndex, new ParaInstrText("T"));
		oRun.Add_ToContent(++nIndex, new ParaInstrText("O"));
		oRun.Add_ToContent(++nIndex, new ParaInstrText("C"));
		oRun.Add_ToContent(++nIndex, new ParaFieldChar(fldchartype_Separate, this));
		oRun.Add_ToContent(++nIndex, new ParaText("T"));
		oRun.Add_ToContent(++nIndex, new ParaText("a"));
		oRun.Add_ToContent(++nIndex, new ParaText("b"));
		oRun.Add_ToContent(++nIndex, new ParaText("l"));
		oRun.Add_ToContent(++nIndex, new ParaText("e"));
		oRun.Add_ToContent(++nIndex, new ParaSpace());
		oRun.Add_ToContent(++nIndex, new ParaText("o"));
		oRun.Add_ToContent(++nIndex, new ParaText("f"));
		oRun.Add_ToContent(++nIndex, new ParaSpace());
		oRun.Add_ToContent(++nIndex, new ParaText("C"));
		oRun.Add_ToContent(++nIndex, new ParaText("o"));
		oRun.Add_ToContent(++nIndex, new ParaText("n"));
		oRun.Add_ToContent(++nIndex, new ParaText("t"));
		oRun.Add_ToContent(++nIndex, new ParaText("e"));
		oRun.Add_ToContent(++nIndex, new ParaText("n"));
		oRun.Add_ToContent(++nIndex, new ParaText("t"));
		oRun.Add_ToContent(++nIndex, new ParaText("s"));
		oRun.Add_ToContent(++nIndex, new ParaFieldChar(fldchartype_End, this));
		oParagraph.Add(oRun);
		return true;
	}
	else if (fieldtype_PAGEREF === nType)
	{
		var oParagraph = this.GetCurrentParagraph();
		if (!oParagraph)
			return false;

		var nIndex = -1;

		var oRun = new ParaRun();
		oRun.Add_ToContent(++nIndex, new ParaFieldChar(fldchartype_Begin, this));
		oRun.Add_ToContent(++nIndex, new ParaInstrText("P"));
		oRun.Add_ToContent(++nIndex, new ParaInstrText("A"));
		oRun.Add_ToContent(++nIndex, new ParaInstrText("G"));
		oRun.Add_ToContent(++nIndex, new ParaInstrText("E"));
		oRun.Add_ToContent(++nIndex, new ParaInstrText("R"));
		oRun.Add_ToContent(++nIndex, new ParaInstrText("E"));
		oRun.Add_ToContent(++nIndex, new ParaInstrText("F"));
		oRun.Add_ToContent(++nIndex, new ParaInstrText(" "));
		oRun.Add_ToContent(++nIndex, new ParaInstrText("T"));
		oRun.Add_ToContent(++nIndex, new ParaInstrText("e"));
		oRun.Add_ToContent(++nIndex, new ParaInstrText("s"));
		oRun.Add_ToContent(++nIndex, new ParaInstrText("t"));
		oRun.Add_ToContent(++nIndex, new ParaInstrText(" "));
		oRun.Add_ToContent(++nIndex, new ParaInstrText("\\"));
		oRun.Add_ToContent(++nIndex, new ParaInstrText("p"));
		oRun.Add_ToContent(++nIndex, new ParaFieldChar(fldchartype_Separate, this));
		oRun.Add_ToContent(++nIndex, new ParaText("1"));
		oRun.Add_ToContent(++nIndex, new ParaFieldChar(fldchartype_End, this));
		oParagraph.Add(oRun);
		return true;
	}

	return false;
};
CDocument.prototype.UpdateComplexField = function(oField)
{
	if (!oField)
		return;

	oField.Update();
};
CDocument.prototype.GetCurrentComplexFields = function()
{
	var oParagraph = this.GetCurrentParagraph();
	if (!oParagraph)
		return [];

	return oParagraph.GetCurrentComplexFields();
};
CDocument.prototype.IsFastCollaboartionBeforeViewModeInReview = function()
{
	return this.ViewModeInReview.isFastCollaboration;
};
CDocument.prototype.CheckComplexFieldsInSelection = function()
{
	if (true !== this.Selection.Use)
		return;

	// Смотрим сколько полей открытых в начальной и конечной позициях.
	var oStartPos = this.GetContentPosition(true, true);
	var oEndPos   = this.GetContentPosition(true, false);

	var arrStartComplexFields = this.GetComplexFieldsByContentPos(oStartPos);
	var arrEndComplexFields   = this.GetComplexFieldsByContentPos(oEndPos);

	var arrStartFields = [];
	for (var nIndex = 0, nCount = arrStartComplexFields.length; nIndex < nCount; ++nIndex)
	{
		var bAdd = true;
		for (var nIndex2 = 0, nCount2 = arrEndComplexFields.length; nIndex2 < nCount2; ++nIndex2)
		{
			if (arrStartComplexFields[nIndex] === arrEndComplexFields[nIndex2])
			{
				bAdd = false;
				break;
			}
		}

		if (bAdd)
		{
			arrStartFields.push(arrStartComplexFields[nIndex]);
		}
	}

	var arrEndFields = [];
	for (var nIndex = 0, nCount = arrEndComplexFields.length; nIndex < nCount; ++nIndex)
	{
		var bAdd = true;
		for (var nIndex2 = 0, nCount2 = arrStartComplexFields.length; nIndex2 < nCount2; ++nIndex2)
		{
			if (arrEndComplexFields[nIndex] === arrStartComplexFields[nIndex2])
			{
				bAdd = false;
				break;
			}
		}

		if (bAdd)
		{
			arrEndFields.push(arrEndComplexFields[nIndex]);
		}
	}

	var nDirection = this.GetSelectDirection();
	if (nDirection > 0)
	{
		if (arrStartFields.length > 0 && arrStartFields[0].IsValid())
			oStartPos = arrStartFields[0].GetStartDocumentPosition();

		if (arrEndFields.length > 0 && arrEndFields[0].IsValid())
			oEndPos = arrEndFields[0].GetEndDocumentPosition();
	}
	else
	{
		if (arrStartFields.length > 0 && arrStartFields[0].IsValid())
			oStartPos = arrStartFields[0].GetEndDocumentPosition();

		if (arrEndFields.length > 0 && arrEndFields[0].IsValid())
			oEndPos = arrEndFields[0].GetStartDocumentPosition();
	}

	this.SetContentSelection(oStartPos, oEndPos, 0, 0, 0);
};
CDocument.prototype.GetFieldsManager = function()
{
	return this.FieldsManager;
};
CDocument.prototype.GetComplexFieldsByContentPos = function(oDocPos)
{
	if (!oDocPos)
		return [];

	var oCurrentDocPos = this.GetContentPosition(false);
	this.SetContentPosition(oDocPos, 0, 0);

	var oCurrentParagraph = this.controller_GetCurrentParagraph(true, null);
	if (!oCurrentParagraph)
		return [];

	var arrComplexFields = oCurrentParagraph.GetCurrentComplexFields();
	this.SetContentPosition(oCurrentDocPos, 0, 0);

	return arrComplexFields;
};
CDocument.prototype.GetBookmarksManager = function()
{
	return this.BookmarksManager;
};
CDocument.prototype.UpdateBookmarks = function()
{
	if (!this.BookmarksManager.IsNeedUpdate())
		return;

	this.BookmarksManager.BeginCollectingProcess();

	for (var nIndex = 0, nCount = this.Content.length; nIndex < nCount; ++nIndex)
	{
		this.Content[nIndex].UpdateBookmarks(this.BookmarksManager);
	}

	this.BookmarksManager.EndCollectingProcess();
};
CDocument.prototype.AddBookmark = function(sName)
{
	var arrBookmarkChars = this.BookmarksManager.GetBookmarkByName(sName);

	var oStartPara = null,
		oEndPara   = null;
	var arrParagraphs = [];
	if (true === this.IsSelectionUse())
	{
		var arrSelectedParagraphs = this.GetCurrentParagraph(false, true);
		if (arrSelectedParagraphs.length > 1)
		{
			arrParagraphs.push(arrSelectedParagraphs[0]);
			arrParagraphs.push(arrSelectedParagraphs[arrSelectedParagraphs.length - 1]);

			oStartPara = arrSelectedParagraphs[0];
			oEndPara   = arrSelectedParagraphs[arrSelectedParagraphs.length - 1];
		}
		else if (arrSelectedParagraphs.length === 1)
		{
			arrParagraphs.push(arrSelectedParagraphs[0]);

			oStartPara = arrSelectedParagraphs[0];
			oEndPara   = arrSelectedParagraphs[0];
		}
	}
	else
	{
		var oCurrentParagraph = this.GetCurrentParagraph(true);
		if (oCurrentParagraph)
		{
			arrParagraphs.push(oCurrentParagraph);
			oStartPara = oCurrentParagraph;
		}
	}

	if (arrParagraphs.length <= 0)
		return;

	if (arrBookmarkChars)
	{
		var oStartPara = arrBookmarkChars[0].GetParagraph();
		var oEndPara   = arrBookmarkChars[1].GetParagraph();

		if (oStartPara)
			arrParagraphs.push(oStartPara);

		if (oEndPara)
			arrParagraphs.push(oEndPara);
	}

	if (false === this.Document_Is_SelectionLocked(changestype_None, {Type : AscCommon.changestype_2_ElementsArray_and_Type, Elements : arrParagraphs, CheckType : changestype_Paragraph_Content}, true))
	{
		this.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddBookmark);

		if (this.BookmarksManager.HaveBookmark(sName))
			this.private_RemoveBookmark(sName);

		var sBookmarkId = this.BookmarksManager.GetNewBookmarkId();

		if (true === this.IsSelectionUse())
		{
			var nDirection = this.GetSelectDirection();
			if (nDirection > 0)
			{
				oEndPara.AddBookmarkChar(new CParagraphBookmark(false, sBookmarkId, sName), true, false);
				oStartPara.AddBookmarkChar(new CParagraphBookmark(true, sBookmarkId, sName), true, true);
			}
			else
			{
				oEndPara.AddBookmarkChar(new CParagraphBookmark(false, sBookmarkId, sName), true, true);
				oStartPara.AddBookmarkChar(new CParagraphBookmark(true, sBookmarkId, sName), true, false);
			}
		}
		else
		{
			oStartPara.AddBookmarkChar(new CParagraphBookmark(false, sBookmarkId, sName), false);
			oStartPara.AddBookmarkChar(new CParagraphBookmark(true, sBookmarkId, sName), false);
		}

		// TODO: Здесь добавляются просто метки закладок, нужно сделать упрощенный пересчет
		this.Recalculate();
	}

};
CDocument.prototype.RemoveBookmark = function(sName)
{

};
CDocument.prototype.private_RemoveBookmark = function(sName)
{

};

function CDocumentSelectionState()
{
    this.Id        = null;
    this.Type      = docpostype_Content;
    this.Data      = {}; // Объект с текущей позицией
}

function CDocumentSectionsInfo()
{
    this.Elements = [];
}

CDocumentSectionsInfo.prototype =
{
    Add : function( SectPr, Index )
    {
        this.Elements.push( new CDocumentSectionsInfoElement( SectPr, Index ) );
    },

    Get_SectionsCount : function()
    {
        return this.Elements.length;
    },

    Clear : function()
    {
        this.Elements.length = 0;
    },

    Find_ByHdrFtr : function(HdrFtr)
    {
        var Count = this.Elements.length;
        for ( var Index = 0; Index < Count; Index++ )
        {
            var SectPr = this.Elements[Index].SectPr;

            if ( HdrFtr === SectPr.Get_Header_First() || HdrFtr === SectPr.Get_Header_Default() || HdrFtr === SectPr.Get_Header_Even() ||
                 HdrFtr === SectPr.Get_Footer_First() || HdrFtr === SectPr.Get_Footer_Default() || HdrFtr === SectPr.Get_Footer_Even() )
                    return Index;
        }

        return -1;
    },

    Get_AllHdrFtrs : function()
    {
        var HdrFtrs = [];

        var Count = this.Elements.length;
        for (var Index = 0; Index < Count; Index++)
        {
            var SectPr = this.Elements[Index].SectPr;
            SectPr.Get_AllHdrFtrs(HdrFtrs);
        }

        return HdrFtrs;
    },

    Reset_HdrFtrRecalculateCache : function()
    {
        var Count = this.Elements.length;
        for ( var Index = 0; Index < Count; Index++ )
        {
            var SectPr = this.Elements[Index].SectPr;

            if ( null != SectPr.HeaderFirst )
                SectPr.HeaderFirst.Reset_RecalculateCache();

            if ( null != SectPr.HeaderDefault )
                SectPr.HeaderDefault.Reset_RecalculateCache();

            if ( null != SectPr.HeaderEven )
                SectPr.HeaderEven.Reset_RecalculateCache();

            if ( null != SectPr.FooterFirst )
                SectPr.FooterFirst.Reset_RecalculateCache();

            if ( null != SectPr.FooterDefault )
                SectPr.FooterDefault.Reset_RecalculateCache();

            if ( null != SectPr.FooterEven )
                SectPr.FooterEven.Reset_RecalculateCache();
        }
    },

    GetAllParagraphs : function(Props, ParaArray)
    {
        var Count = this.Elements.length;
        for ( var Index = 0; Index < Count; Index++ )
        {
            var SectPr = this.Elements[Index].SectPr;

            if ( null != SectPr.HeaderFirst )
                SectPr.HeaderFirst.GetAllParagraphs(Props, ParaArray);

            if ( null != SectPr.HeaderDefault )
                SectPr.HeaderDefault.GetAllParagraphs(Props, ParaArray);

            if ( null != SectPr.HeaderEven )
                SectPr.HeaderEven.GetAllParagraphs(Props, ParaArray);

            if ( null != SectPr.FooterFirst )
                SectPr.FooterFirst.GetAllParagraphs(Props, ParaArray);

            if ( null != SectPr.FooterDefault )
                SectPr.FooterDefault.GetAllParagraphs(Props, ParaArray);

            if ( null != SectPr.FooterEven )
                SectPr.FooterEven.GetAllParagraphs(Props, ParaArray);
        }
    },

	GetAllDrawingObjects : function(arrDrawings)
    {
        for (var nIndex = 0, nCount = this.Elements.length; nIndex < nCount; ++nIndex)
        {
            var SectPr = this.Elements[nIndex].SectPr;

            if (null != SectPr.HeaderFirst)
                SectPr.HeaderFirst.GetAllDrawingObjects(arrDrawings);

            if (null != SectPr.HeaderDefault)
                SectPr.HeaderDefault.GetAllDrawingObjects(arrDrawings);

            if (null != SectPr.HeaderEven)
                SectPr.HeaderEven.GetAllDrawingObjects(arrDrawings);

            if (null != SectPr.FooterFirst)
                SectPr.FooterFirst.GetAllDrawingObjects(arrDrawings);

            if (null != SectPr.FooterDefault)
                SectPr.FooterDefault.GetAllDrawingObjects(arrDrawings);

            if (null != SectPr.FooterEven)
                SectPr.FooterEven.GetAllDrawingObjects(arrDrawings);
        }
    },

    Document_CreateFontMap : function(FontMap)
    {
        var Count = this.Elements.length;
        for ( var Index = 0; Index < Count; Index++ )
        {
            var SectPr = this.Elements[Index].SectPr;

            if ( null != SectPr.HeaderFirst )
                SectPr.HeaderFirst.Document_CreateFontMap(FontMap);

            if ( null != SectPr.HeaderDefault )
                SectPr.HeaderDefault.Document_CreateFontMap(FontMap);

            if ( null != SectPr.HeaderEven )
                SectPr.HeaderEven.Document_CreateFontMap(FontMap);

            if ( null != SectPr.FooterFirst )
                SectPr.FooterFirst.Document_CreateFontMap(FontMap);

            if ( null != SectPr.FooterDefault )
                SectPr.FooterDefault.Document_CreateFontMap(FontMap);

            if ( null != SectPr.FooterEven )
                SectPr.FooterEven.Document_CreateFontMap(FontMap);
        }
    },

    Document_CreateFontCharMap : function(FontCharMap)
    {
        var Count = this.Elements.length;
        for ( var Index = 0; Index < Count; Index++ )
        {
            var SectPr = this.Elements[Index].SectPr;

            if ( null != SectPr.HeaderFirst )
                SectPr.HeaderFirst.Document_CreateFontCharMap(FontCharMap);

            if ( null != SectPr.HeaderDefault )
                SectPr.HeaderDefault.Document_CreateFontCharMap(FontCharMap);

            if ( null != SectPr.HeaderEven )
                SectPr.HeaderEven.Document_CreateFontCharMap(FontCharMap);

            if ( null != SectPr.FooterFirst )
                SectPr.FooterFirst.Document_CreateFontCharMap(FontCharMap);

            if ( null != SectPr.FooterDefault )
                SectPr.FooterDefault.Document_CreateFontCharMap(FontCharMap);

            if ( null != SectPr.FooterEven )
                SectPr.FooterEven.Document_CreateFontCharMap(FontCharMap);
        }
    },

    Document_Get_AllFontNames : function ( AllFonts )
    {
        var Count = this.Elements.length;
        for ( var Index = 0; Index < Count; Index++ )
        {
            var SectPr = this.Elements[Index].SectPr;

            if ( null != SectPr.HeaderFirst )
                SectPr.HeaderFirst.Document_Get_AllFontNames(AllFonts);

            if ( null != SectPr.HeaderDefault )
                SectPr.HeaderDefault.Document_Get_AllFontNames(AllFonts);

            if ( null != SectPr.HeaderEven )
                SectPr.HeaderEven.Document_Get_AllFontNames(AllFonts);

            if ( null != SectPr.FooterFirst )
                SectPr.FooterFirst.Document_Get_AllFontNames(AllFonts);

            if ( null != SectPr.FooterDefault )
                SectPr.FooterDefault.Document_Get_AllFontNames(AllFonts);

            if ( null != SectPr.FooterEven )
                SectPr.FooterEven.Document_Get_AllFontNames(AllFonts);
        }
    },

    Get_Index : function(Index)
    {
        var Count = this.Elements.length;

        for ( var Pos = 0; Pos < Count; Pos++ )
        {
            if ( Index <= this.Elements[Pos].Index )
                return Pos;
        }

        // Последний элемент здесь это всегда конечная секция документа
        return (Count - 1);
    },

    Get_Count : function()
    {
        return this.Elements.length;
    },

    Get_SectPr : function(Index)
    {
        var Count = this.Elements.length;

        for ( var Pos = 0; Pos < Count; Pos++ )
        {
            if ( Index <= this.Elements[Pos].Index )
                return this.Elements[Pos];
        }

        // Последний элемент здесь это всегда конечная секция документа
        return this.Elements[Count - 1];
    },

    Get_SectPr2 : function(Index)
    {
        return this.Elements[Index];
    },

    Find : function(SectPr)
    {
        var Count = this.Elements.length;
        for ( var Index = 0; Index < Count; Index++ )
        {
            var Element = this.Elements[Index];
            if ( Element.SectPr === SectPr )
                return Index;
        }

        return -1;
    },

    Update_OnAdd : function(Pos, Items)
    {
        var Count = Items.length;
        var Len = this.Elements.length;

        // Сначала обновим старые метки
        for (var Index = 0; Index < Len; Index++)
        {
            if ( this.Elements[Index].Index >= Pos )
                this.Elements[Index].Index += Count;
        }

        // Если среди новых элементов были параграфы с настройками секции, тогда добавим их здесь
        for (var Index = 0; Index < Count; Index++ )
        {
            var Item = Items[Index];
            var SectPr = ( type_Paragraph === Item.GetType() ? Item.Get_SectionPr() : undefined );

            if ( undefined !== SectPr )
            {
                var TempPos = 0;
                for ( ; TempPos < Len; TempPos++ )
                {
                    if ( Pos + Index <= this.Elements[TempPos].Index )
                        break;
                }

                this.Elements.splice( TempPos, 0, new CDocumentSectionsInfoElement( SectPr, Pos + Index ) );
                Len++;
            }
        }
    },

    Update_OnRemove : function(Pos, Count, bCheckHdrFtr)
    {
        var Len = this.Elements.length;

        for (var Index = 0; Index < Len; Index++)
        {
            var CurPos = this.Elements[Index].Index;

            if (CurPos >= Pos && CurPos < Pos + Count)
            {
                // Копируем поведение Word: Если у следующей секции не задан вообще ни один колонтитул,
                // тогда копируем ссылки на колонтитулы из удаляемой секции. Если задан хоть один колонтитул,
                // тогда этого не делаем.
                if (true === bCheckHdrFtr && Index < Len - 1)
                {
                    var CurrSectPr = this.Elements[Index].SectPr;
                    var NextSectPr = this.Elements[Index + 1].SectPr;
                    if (true === NextSectPr.Is_AllHdrFtrNull() && true !== CurrSectPr.Is_AllHdrFtrNull())
                    {
                        NextSectPr.Set_Header_First(CurrSectPr.Get_Header_First());
                        NextSectPr.Set_Header_Even(CurrSectPr.Get_Header_Even());
                        NextSectPr.Set_Header_Default(CurrSectPr.Get_Header_Default());
                        NextSectPr.Set_Footer_First(CurrSectPr.Get_Footer_First());
                        NextSectPr.Set_Footer_Even(CurrSectPr.Get_Footer_Even());
                        NextSectPr.Set_Footer_Default(CurrSectPr.Get_Footer_Default());
                    }
                }

                this.Elements.splice(Index, 1);
                Len--;
                Index--;


            }
            else if (CurPos >= Pos + Count)
                this.Elements[Index].Index -= Count;
        }
    }
};
CDocumentSectionsInfo.prototype.GetAllContentControls = function(arrContentControls)
{
	for (var nIndex = 0, nCount = this.Elements.length; nIndex < nCount; ++nIndex)
	{
		var SectPr = this.Elements[nIndex].SectPr;

		if (null != SectPr.HeaderFirst)
			SectPr.HeaderFirst.GetAllContentControls(arrContentControls);

		if (null != SectPr.HeaderDefault)
			SectPr.HeaderDefault.GetAllContentControls(arrContentControls);

		if (null != SectPr.HeaderEven)
			SectPr.HeaderEven.GetAllContentControls(arrContentControls);

		if (null != SectPr.FooterFirst)
			SectPr.FooterFirst.GetAllContentControls(arrContentControls);

		if (null != SectPr.FooterDefault)
			SectPr.FooterDefault.GetAllContentControls(arrContentControls);

		if (null != SectPr.FooterEven)
			SectPr.FooterEven.GetAllContentControls(arrContentControls);
	}
};

function CDocumentSectionsInfoElement(SectPr, Index)
{
    this.SectPr = SectPr;
    this.Index  = Index;
}

function CDocumentCompareDrawingsLogicPositions(Drawing1, Drawing2)
{
    this.Drawing1 = Drawing1;
    this.Drawing2 = Drawing2;
    this.Result   = 0;
}

function CTrackRevisionsManager(LogicDocument)
{
    this.LogicDocument = LogicDocument;
    this.CheckPara     = {}; // Параграфы, которые нужно проверить
    this.Changes       = {}; // Объект с ключом - Id параграфа, в котором лежит массив изменений

    this.CurChange     = null; // Текущеее изменение
    this.CurPara       = null; // Параграф с текущим изменением

    this.VisibleChanges = []; // Изменения, которые отображаются в сплывающем окне
    this.OldVisibleChanges = [];
}

CTrackRevisionsManager.prototype.Check_Paragraph = function(Para)
{
    var ParaId = Para.Get_Id();
    if (undefined == this.CheckPara[ParaId])
        this.CheckPara[ParaId] = 1;
    else
        this.CheckPara[ParaId]++;
};
CTrackRevisionsManager.prototype.Add_Change = function(ParaId, Change)
{
    if (undefined === this.Changes[ParaId])
        this.Changes[ParaId] = [];

    this.Changes[ParaId].push(Change);
};
CTrackRevisionsManager.prototype.Get_ParagraphChanges = function(ParaId)
{
    if (this.Changes[ParaId])
        return this.Changes[ParaId];

    return [];
};
CTrackRevisionsManager.prototype.Continue_TrackRevisions = function()
{
    var bNeedUpdate = false;
    for (var ParaId in this.CheckPara)
    {
        delete this.CheckPara[ParaId];
        var Para = g_oTableId.Get_ById(ParaId);
        if (Para && Para instanceof Paragraph && Para.Is_UseInDocument())
        {
            delete this.Changes[ParaId];
            Para.Check_RevisionsChanges(this);
            bNeedUpdate = true;
        }
    }

    if (bNeedUpdate)
        this.LogicDocument.Document_UpdateInterfaceState();
};
CTrackRevisionsManager.prototype.Get_NextChange = function()
{
    var OldCurChange = this.CurChange;
    var OldCurPara   = this.CurPara;

    var NextPara = null;
    if (null !== this.CurChange && null !== this.CurPara)
    {
        var ChangesArray = this.Changes[this.CurPara.Get_Id()];
        var ChangeIndex = -1;
        for (var Index = 0, Count = ChangesArray.length; Index < Count; Index++)
        {
            if (this.CurChange === ChangesArray[Index])
            {
                ChangeIndex = Index;
                break;
            }
        }

        if (-1 !== ChangeIndex && ChangeIndex < ChangesArray.length - 1)
        {
            this.CurChange = ChangesArray[ChangeIndex + 1];
            return this.CurChange;
        }

        NextPara = this.LogicDocument.GetRevisionsChangeParagraph(1, this.CurPara);
    }
    else
    {
        var SearchEngine = this.LogicDocument.private_GetRevisionsChangeParagraph(1, null);
        NextPara = SearchEngine.Get_FoundedParagraph();
        if (null !== NextPara && NextPara === SearchEngine.GetCurrentParagraph())
        {
            var NextChangesArray = this.Changes[NextPara.Get_Id()];
            if (undefined !== NextChangesArray && NextChangesArray.length > 0)
            {
                var ParaContentPos = NextPara.Get_ParaContentPos(NextPara.IsSelectionUse(), true);
                for (var ChangeIndex = 0, Count = NextChangesArray.length; ChangeIndex < Count; ChangeIndex++)
                {
                    var ChangeEndPos = NextChangesArray[ChangeIndex].get_EndPos();
                    if (ParaContentPos.Compare(ChangeEndPos) <= 0)
                    {
                        this.CurChange = NextChangesArray[ChangeIndex];
                        this.CurPara   = NextPara;
                        return this.CurChange;
                    }
                }
                NextPara = this.LogicDocument.GetRevisionsChangeParagraph(1, NextPara);
            }
        }
    }

    if (null !== NextPara)
    {
        var NextChangesArray = this.Changes[NextPara.Get_Id()];
        if (undefined !== NextChangesArray && NextChangesArray.length > 0)
        {
            this.CurChange = NextChangesArray[0];
            this.CurPara   = NextPara;
            return this.CurChange;
        }
    }

    if (null !== OldCurChange && null !== OldCurPara)
    {
        this.CurChange = OldCurChange;
        this.CurPara   = OldCurPara;
        return OldCurChange;
    }

    this.CurChange = null;
    this.CurPara   = null;
    return null;
};
CTrackRevisionsManager.prototype.Get_PrevChange = function()
{
    var OldCurChange = this.CurChange;
    var OldCurPara   = this.CurPara;

    var PrevPara = null;
    if (null !== this.CurChange && null !== this.CurPara)
    {
        var ChangesArray = this.Changes[this.CurPara.Get_Id()];
        var ChangeIndex = -1;
        for (var Index = 0, Count = ChangesArray.length; Index < Count; Index++)
        {
            if (this.CurChange === ChangesArray[Index])
            {
                ChangeIndex = Index;
                break;
            }
        }

        if (-1 !== ChangeIndex && ChangeIndex > 0)
        {
            this.CurChange = ChangesArray[ChangeIndex - 1];
            return this.CurChange;
        }

        PrevPara = this.LogicDocument.GetRevisionsChangeParagraph(-1, this.CurPara);
    }
    else
    {
        var SearchEngine = this.LogicDocument.private_GetRevisionsChangeParagraph(-1, null);
        PrevPara = SearchEngine.Get_FoundedParagraph();
        if (null !== PrevPara && PrevPara === SearchEngine.GetCurrentParagraph())
        {
            var PrevChangesArray = this.Changes[PrevPara.Get_Id()];
            if (undefined !== PrevChangesArray && PrevChangesArray.length > 0)
            {
                var ParaContentPos = PrevPara.Get_ParaContentPos(PrevPara.IsSelectionUse(), true);
                for (var ChangeIndex = PrevChangesArray.length - 1; ChangeIndex >= 0; ChangeIndex--)
                {
                    var ChangeStartPos = PrevChangesArray[ChangeIndex].get_StartPos();
                    if (ParaContentPos.Compare(ChangeStartPos) >= 0)
                    {
                        this.CurChange = PrevChangesArray[ChangeIndex];
                        this.CurPara   = PrevPara;
                        return this.CurChange;
                    }
                }

                PrevPara = this.LogicDocument.GetRevisionsChangeParagraph(-1, PrevPara);
            }
        }
    }

    if (null !== PrevPara)
    {
        var PrevChangesArray = this.Changes[PrevPara.Get_Id()];
        if (undefined !== PrevChangesArray && PrevChangesArray.length > 0)
        {
            this.CurChange = PrevChangesArray[PrevChangesArray.length - 1];
            this.CurPara = PrevPara;
            return this.CurChange;
        }
    }

    if (null !== OldCurChange && null !== OldCurPara)
    {
        this.CurChange = OldCurChange;
        this.CurPara   = OldCurPara;
        return OldCurChange;
    }

    this.CurChange = null;
    this.CurPara   = null;
    return null;
};
CTrackRevisionsManager.prototype.Have_Changes = function()
{
    for (var ParaId in this.Changes)
    {
        if (this.Changes[ParaId].length > 0)
            return true;
    }

    return false;
};
CTrackRevisionsManager.prototype.Clear_CurrentChange = function()
{
    this.CurChange = null;
    this.CurPara   = null;
};
CTrackRevisionsManager.prototype.Get_CurrentChangeParagraph = function()
{
    return this.CurPara;
};
CTrackRevisionsManager.prototype.Get_CurrentChange = function()
{
    return this.CurChange;
};
CTrackRevisionsManager.prototype.Clear_VisibleChanges = function()
{
	if (this.VisibleChanges.length > 0)
	{
		var oEditorApi = this.LogicDocument.Get_Api();
		oEditorApi.sync_BeginCatchRevisionsChanges();
		oEditorApi.sync_EndCatchRevisionsChanges();
	}

    this.VisibleChanges = [];
};
CTrackRevisionsManager.prototype.Add_VisibleChange = function(Change)
{
    this.VisibleChanges.push(Change);
};
CTrackRevisionsManager.prototype.Get_VisibleChanges = function()
{
    return this.VisibleChanges;
};
CTrackRevisionsManager.prototype.Begin_CollectChanges = function(bSaveCurrentChange)
{
    if (true === this.private_HaveParasToCheck())
        return;

    if (true !== bSaveCurrentChange)
        this.Clear_CurrentChange();

    this.OldVisibleChanges = this.VisibleChanges;
    this.VisibleChanges = [];
};
CTrackRevisionsManager.prototype.End_CollectChanges = function(oEditor)
{
    if (true === this.private_HaveParasToCheck())
        return;

    if (null !== this.CurChange)
        this.VisibleChanges = [this.CurChange];

    var bMove = false;
    var bChange = false;

    var Len = this.VisibleChanges.length;
    if (this.OldVisibleChanges.length !== Len)
    {
        bChange = true;
    }
    else if (0 !== Len)
    {
        for (var ChangeIndex = 0; ChangeIndex < Len; ChangeIndex++)
        {
            if (this.OldVisibleChanges[ChangeIndex] !== this.VisibleChanges[ChangeIndex])
            {
                bChange = true;
                break;
            }
            else if (true !== this.VisibleChanges[ChangeIndex].ComparePrevPosition())
            {
                bMove = true;
            }
        }
    }

    if (true === bChange)
    {
        oEditor.sync_BeginCatchRevisionsChanges();

        if (Len > 0)
        {
            var Pos = this.private_GetVisibleChangesXY();
            for (var ChangeIndex = 0; ChangeIndex < Len; ChangeIndex++)
            {
                var Change = this.VisibleChanges[ChangeIndex];
                Change.put_XY(Pos.X, Pos.Y);
                oEditor.sync_AddRevisionsChange(Change);
            }
        }
        oEditor.sync_EndCatchRevisionsChanges();
    }
    else if (true === bMove)
    {
        this.Update_VisibleChangesPosition(oEditor);
    }
};
CTrackRevisionsManager.prototype.Update_VisibleChangesPosition = function(oEditor)
{
    if (this.VisibleChanges.length > 0)
    {
        var Pos = this.private_GetVisibleChangesXY();
        oEditor.sync_UpdateRevisionsChangesPosition(Pos.X, Pos.Y);
    }
};
CTrackRevisionsManager.prototype.private_GetVisibleChangesXY = function()
{
    if (this.VisibleChanges.length > 0)
    {
        var Change = this.VisibleChanges[0];
        var Change_X       = Change.get_InternalPosX();
        var Change_Y       = Change.get_InternalPosY();
        var Change_PageNum = Change.get_InternalPosPageNum();
        var Change_Para    = Change.get_Paragraph();
        if (Change_Para && Change_Para.DrawingDocument)
        {
            var TextTransform = (Change_Para ? Change_Para.Get_ParentTextTransform() : undefined);
            if (TextTransform)
                Change_Y = TextTransform.TransformPointY(Change_X, Change_Y);

            var Coords = Change_Para.DrawingDocument.ConvertCoordsToCursorWR(Change_X, Change_Y, Change_PageNum);
            return {X : Coords.X, Y : Coords.Y};
        }
    }

    return {X : 0, Y : 0};
};
CTrackRevisionsManager.prototype.Get_AllChangesLogicDocuments = function()
{
    this.Continue_TrackRevisions();
    var LogicDocuments = {};

    for (var ParaId in this.Changes)
    {
        var Para = g_oTableId.Get_ById(ParaId);
        if (Para && Para.Get_Parent())
        {
            LogicDocuments[Para.Get_Parent().Get_Id()] = true;
        }
    }

    return LogicDocuments;
};
CTrackRevisionsManager.prototype.Get_ChangeRelatedParagraphs = function(Change, bAccept)
{
    var RelatedParas = {};
    this.private_GetChangeRelatedParagraphs(Change, bAccept, RelatedParas);
    return this.private_ConvertParagraphsObjectToArray(RelatedParas);
};
CTrackRevisionsManager.prototype.private_GetChangeRelatedParagraphs = function(Change, bAccept, RelatedParas)
{
    if (undefined !== Change)
    {
        var Type = Change.get_Type();
        var Para = Change.get_Paragraph();
        if (Para)
        {
            RelatedParas[Para.Get_Id()] = true;
            if ((c_oAscRevisionsChangeType.ParaAdd === Type && true !== bAccept) || (c_oAscRevisionsChangeType.ParaRem === Type && true === bAccept))
            {
                var LogicDocument = Para.Get_Parent();
                var ParaIndex = Para.Get_Index();

                if (LogicDocument && -1 !== ParaIndex)
                {
                    if (ParaIndex < LogicDocument.Get_ElementsCount() - 1)
                    {
                        var Element = LogicDocument.Get_ElementByIndex(ParaIndex + 1);
                        if (Element && type_Paragraph === Element.Get_Type())
                            RelatedParas[Element.Get_Id()] = true;
                    }
                }
            }
        }
    }
};
CTrackRevisionsManager.prototype.private_ConvertParagraphsObjectToArray = function(ParagraphsObject)
{
    var ParagraphsArray = [];
    for (var ParaId in ParagraphsObject)
    {
        var Para = g_oTableId.Get_ById(ParaId);
        if (null !== Para)
        {
            ParagraphsArray.push(Para);
        }
    }
    return ParagraphsArray;
};
CTrackRevisionsManager.prototype.Get_AllChangesRelatedParagraphs = function(bAccept)
{
    var RelatedParas = {};
    for (var ParaId in this.Changes)
    {
        for (var ChangeIndex = 0, ChangesCount = this.Changes[ParaId].length; ChangeIndex < ChangesCount; ++ChangeIndex)
        {
            var Change = this.Changes[ParaId][ChangeIndex];
            this.private_GetChangeRelatedParagraphs(Change, bAccept, RelatedParas);
        }
    }
    return this.private_ConvertParagraphsObjectToArray(RelatedParas);
};
CTrackRevisionsManager.prototype.Get_AllChangesRelatedParagraphsBySelectedParagraphs = function(SelectedParagraphs, bAccept)
{
    var RelatedParas = {};
    for (var ParaIndex = 0, ParasCount = SelectedParagraphs.length; ParaIndex < ParasCount; ++ParaIndex)
    {
        var Para = SelectedParagraphs[ParaIndex];
        var ParaId = Para.Get_Id();
        if (this.Changes[ParaId] && this.Changes[ParaId].length > 0)
        {
            RelatedParas[ParaId] = true;
            if (true === Para.Selection_CheckParaEnd())
            {
                var CheckNext = false;
                for (var ChangeIndex = 0, ChangesCount = this.Changes[ParaId].length; ChangeIndex < ChangesCount; ++ChangeIndex)
                {
                    var ChangeType = this.Changes[ParaId][ChangeIndex].get_Type();
                    if ((c_oAscRevisionsChangeType.ParaAdd === ChangeType && true !== bAccept) || (c_oAscRevisionsChangeType.ParaRem === ChangeType && true === bAccept))
                    {
                        CheckNext = true;
                        break;
                    }
                }

                if (true === CheckNext)
                {
                    var NextElement = Para.Get_DocumentNext();
                    if (null !== NextElement && type_Paragraph === NextElement.Get_Type())
                    {
                        RelatedParas[NextElement.Get_Id()] = true;
                    }
                }
            }
        }
    }
    return this.private_ConvertParagraphsObjectToArray(RelatedParas);
};
CTrackRevisionsManager.prototype.private_HaveParasToCheck = function()
{
    for (var ParaId in this.CheckPara)
    {
        var Para = g_oTableId.Get_ById(ParaId);
        if (Para && Para instanceof Paragraph && Para.Is_UseInDocument())
            return true;
    }

    return false;
};
CTrackRevisionsManager.prototype.Get_AllChanges = function()
{
	this.Continue_TrackRevisions();
	return this.Changes;
};

function CRevisionsChangeParagraphSearchEngine(Direction, CurrentPara, TrackManager)
{
    this.TrackManager = TrackManager;
    this.Direction    = Direction;
    this.CurrentPara  = CurrentPara;
    this.CurrentFound = false;

    this.Para         = null;
}
CRevisionsChangeParagraphSearchEngine.prototype.Set_CurrentFound = function(Para)
{
    this.CurrentFound = true;
};
CRevisionsChangeParagraphSearchEngine.prototype.Set_CurrentParagraph = function(Para)
{
    this.CurrentPara = Para;
};
CRevisionsChangeParagraphSearchEngine.prototype.Is_CurrentFound = function()
{
    return this.CurrentFound;
};
CRevisionsChangeParagraphSearchEngine.prototype.GetCurrentParagraph = function()
{
    return this.CurrentPara;
};
CRevisionsChangeParagraphSearchEngine.prototype.Set_FoundedParagraph = function(Para)
{
    if (this.TrackManager.Get_ParagraphChanges(Para.Get_Id()).length > 0)
        this.Para = Para;
};
CRevisionsChangeParagraphSearchEngine.prototype.Is_Found = function()
{
    return (null === this.Para ? false : true);
};
CRevisionsChangeParagraphSearchEngine.prototype.Get_FoundedParagraph = function()
{
    return this.Para;
};
CRevisionsChangeParagraphSearchEngine.prototype.Get_Direction = function()
{
    return this.Direction;
};

function CDocumentPagePosition()
{
    this.Page   = 0;
    this.Column = 0;
}

function CDocumentNumberingInfoEngine(ParaId, NumPr, Numbering)
{
    this.ParaId    = ParaId;
    this.NumId     = NumPr.NumId;
    this.Lvl       = NumPr.Lvl;
    this.Numbering = Numbering;
    this.NumInfo   = new Array(this.Lvl + 1);
    this.Restart   = [-1, -1, -1, -1, -1, -1, -1, -1, -1]; // Этот параметр контролирует уровень, начиная с которого делаем рестарт для текущего уровня
    this.PrevLvl   = -1;
    this.Found     = false;

    this.Init();
}

CDocumentNumberingInfoEngine.prototype.Init = function()
{
    for (var Index = 0; Index < this.NumInfo.length; ++Index)
        this.NumInfo[Index] = 0;

    var AbstractNum = null;
    if (undefined !== this.Numbering && null !== (AbstractNum = this.Numbering.Get_AbstractNum(this.NumId)))
    {
        for (var LvlIndex = 0; LvlIndex < 9; LvlIndex++)
            this.Restart[LvlIndex] = AbstractNum.Lvl[LvlIndex].Restart;
    }
};
CDocumentNumberingInfoEngine.prototype.Is_Found = function()
{
    return this.Found;
};
CDocumentNumberingInfoEngine.prototype.Check_Paragraph = function(Para)
{
    var ParaNumPr = Para.Numbering_Get();
    if (undefined !== ParaNumPr && ParaNumPr.NumId === this.NumId && (undefined === Para.Get_SectionPr() || true !== Para.IsEmpty()))
    {
        // Делаем рестарты, если они нужны
        if (-1 !== this.PrevLvl && this.PrevLvl < ParaNumPr.Lvl)
        {
            for ( var Index2 = this.PrevLvl + 1; Index2 < 9; ++Index2)
            {
                if (0 != this.Restart[Index2] && (-1 == this.Restart[Index2] || this.PrevLvl <= (this.Restart[Index2] - 1)))
                    this.NumInfo[Index2] = 0;
            }
        }

        if (undefined === this.NumInfo[ParaNumPr.Lvl])
            this.NumInfo[ParaNumPr.Lvl] = 0;
        else
            this.NumInfo[ParaNumPr.Lvl]++;

        for (var Index2 = ParaNumPr.Lvl - 1; Index2 >= 0; --Index2)
        {
            if (undefined === this.NumInfo[Index2] || 0 === this.NumInfo[Index2])
                this.NumInfo[Index2] = 1;
        }

        this.PrevLvl = ParaNumPr.Lvl;
    }

    if (this.ParaId === Para.Get_Id())
        this.Found = true;
};
CDocumentNumberingInfoEngine.prototype.Get_NumInfo = function()
{
    return this.NumInfo;
};

function CDocumentFootnotesRangeEngine(bExtendedInfo)
{
	this.m_oFirstFootnote = null; // Если не задана ищем с начала
	this.m_oLastFootnote  = null; // Если не задана ищем до конца

	this.m_arrFootnotes  = [];
	this.m_bForceStop    = false;

	this.m_bExtendedInfo = (true === bExtendedInfo ? true : false);
	this.m_arrParagraphs = [];
	this.m_oCurParagraph = null;
	this.m_arrRuns       = [];
	this.m_arrRefs       = [];
}
CDocumentFootnotesRangeEngine.prototype.Init = function(oFirstFootnote, oLastFootnote)
{
	this.m_oFirstFootnote = oFirstFootnote ? oFirstFootnote : null;
	this.m_oLastFootnote  = oLastFootnote ? oLastFootnote : null;
};
CDocumentFootnotesRangeEngine.prototype.Add = function(oFootnote, oFootnoteRef, oRun)
{
	if (!oFootnote || true === this.m_bForceStop)
		return;

	if (this.m_arrFootnotes.length <= 0 && null !== this.m_oFirstFootnote)
	{
		if (this.m_oFirstFootnote === oFootnote)
			this.private_AddFootnote(oFootnote, oFootnoteRef, oRun);
		else if (this.m_oLastFootnote === oFootnote)
			this.m_bForceStop = true;
	}
	else if (this.m_arrFootnotes.length >= 1 && null !== this.m_oLastFootnote)
	{
		if (this.m_oLastFootnote !== this.m_arrFootnotes[this.m_arrFootnotes.length - 1])
			this.private_AddFootnote(oFootnote, oFootnoteRef, oRun);
	}
	else
	{
		this.private_AddFootnote(oFootnote, oFootnoteRef, oRun);
	}
};
CDocumentFootnotesRangeEngine.prototype.IsRangeFull = function()
{
	if (true === this.m_bForceStop)
		return true;

	if (null !== this.m_oLastFootnote && this.m_arrFootnotes.length >= 1 && this.m_oLastFootnote === this.m_arrFootnotes[this.m_arrFootnotes.length - 1])
		return true;

	return false;
};
CDocumentFootnotesRangeEngine.prototype.GetRange = function()
{
	return this.m_arrFootnotes;
};
CDocumentFootnotesRangeEngine.prototype.GetParagraphs = function()
{
	return this.m_arrParagraphs;
};
CDocumentFootnotesRangeEngine.prototype.SetCurrentParagraph = function(oParagraph)
{
	this.m_oCurParagraph = oParagraph;
};
CDocumentFootnotesRangeEngine.prototype.private_AddFootnote = function(oFootnote, oFootnoteRef, oRun)
{
	this.m_arrFootnotes.push(oFootnote);

	if (true === this.m_bExtendedInfo)
	{
		this.m_arrRuns.push(oRun);
		this.m_arrRefs.push(oFootnoteRef);

		// Добавляем в общий список используемых параграфов
		var nCount = this.m_arrParagraphs.length;
		if (nCount <= 0 || this.m_arrParagraphs[nCount - 1] !== this.m_oCurParagraph)
			this.m_arrParagraphs[nCount] = this.m_oCurParagraph;
	}
};
CDocumentFootnotesRangeEngine.prototype.GetRuns = function()
{
	return this.m_arrRuns;
};
CDocumentFootnotesRangeEngine.prototype.GetRefs = function()
{
	return this.m_arrRefs;
};


//-------------------------------------------------------------export---------------------------------------------------
window['Asc'] = window['Asc'] || {};
window['AscCommon'] = window['AscCommon'] || {};
window['AscCommonWord'] = window['AscCommonWord'] || {};
window['AscCommonWord'].CDocument = CDocument;
window['AscCommonWord'].docpostype_Content        = docpostype_Content;
window['AscCommonWord'].docpostype_HdrFtr         = docpostype_HdrFtr;
window['AscCommonWord'].docpostype_DrawingObjects = docpostype_DrawingObjects;
window['AscCommonWord'].docpostype_Footnotes      = docpostype_Footnotes;

window['AscCommon'].Page_Width = Page_Width;
window['AscCommon'].Page_Height = Page_Height;
window['AscCommon'].X_Left_Margin = X_Left_Margin;
window['AscCommon'].X_Right_Margin = X_Right_Margin;
window['AscCommon'].Y_Bottom_Margin = Y_Bottom_Margin;
window['AscCommon'].Y_Top_Margin = Y_Top_Margin;
window['AscCommon'].selectionflag_Common = selectionflag_Common;

CDocumentColumnProps.prototype['put_W']     = CDocumentColumnProps.prototype.put_W;
CDocumentColumnProps.prototype['get_W']     = CDocumentColumnProps.prototype.get_W;
CDocumentColumnProps.prototype['put_Space'] = CDocumentColumnProps.prototype.put_Space;
CDocumentColumnProps.prototype['get_Space'] = CDocumentColumnProps.prototype.get_Space;

window['Asc']['CDocumentColumnsProps'] = CDocumentColumnsProps;
CDocumentColumnsProps.prototype['get_EqualWidth'] = CDocumentColumnsProps.prototype.get_EqualWidth;
CDocumentColumnsProps.prototype['put_EqualWidth'] = CDocumentColumnsProps.prototype.put_EqualWidth;
CDocumentColumnsProps.prototype['get_Num']        = CDocumentColumnsProps.prototype.get_Num       ;
CDocumentColumnsProps.prototype['put_Num']        = CDocumentColumnsProps.prototype.put_Num       ;
CDocumentColumnsProps.prototype['get_Sep']        = CDocumentColumnsProps.prototype.get_Sep       ;
CDocumentColumnsProps.prototype['put_Sep']        = CDocumentColumnsProps.prototype.put_Sep       ;
CDocumentColumnsProps.prototype['get_Space']      = CDocumentColumnsProps.prototype.get_Space     ;
CDocumentColumnsProps.prototype['put_Space']      = CDocumentColumnsProps.prototype.put_Space     ;
CDocumentColumnsProps.prototype['get_ColsCount']  = CDocumentColumnsProps.prototype.get_ColsCount ;
CDocumentColumnsProps.prototype['get_Col']        = CDocumentColumnsProps.prototype.get_Col       ;
CDocumentColumnsProps.prototype['put_Col']        = CDocumentColumnsProps.prototype.put_Col       ;
CDocumentColumnsProps.prototype['put_ColByValue'] = CDocumentColumnsProps.prototype.put_ColByValue;
CDocumentColumnsProps.prototype['get_TotalWidth'] = CDocumentColumnsProps.prototype.get_TotalWidth;

window['Asc']['CDocumentSectionProps'] = window['Asc'].CDocumentSectionProps = CDocumentSectionProps;
CDocumentSectionProps.prototype["get_W"]              = CDocumentSectionProps.prototype.get_W;
CDocumentSectionProps.prototype["put_W"]              = CDocumentSectionProps.prototype.put_W;
CDocumentSectionProps.prototype["get_H"]              = CDocumentSectionProps.prototype.get_H;
CDocumentSectionProps.prototype["put_H"]              = CDocumentSectionProps.prototype.put_H;
CDocumentSectionProps.prototype["get_Orientation"]    = CDocumentSectionProps.prototype.get_Orientation;
CDocumentSectionProps.prototype["put_Orientation"]    = CDocumentSectionProps.prototype.put_Orientation;
CDocumentSectionProps.prototype["get_LeftMargin"]     = CDocumentSectionProps.prototype.get_LeftMargin;
CDocumentSectionProps.prototype["put_LeftMargin"]     = CDocumentSectionProps.prototype.put_LeftMargin;
CDocumentSectionProps.prototype["get_TopMargin"]      = CDocumentSectionProps.prototype.get_TopMargin;
CDocumentSectionProps.prototype["put_TopMargin"]      = CDocumentSectionProps.prototype.put_TopMargin;
CDocumentSectionProps.prototype["get_RightMargin"]    = CDocumentSectionProps.prototype.get_RightMargin;
CDocumentSectionProps.prototype["put_RightMargin"]    = CDocumentSectionProps.prototype.put_RightMargin;
CDocumentSectionProps.prototype["get_BottomMargin"]   = CDocumentSectionProps.prototype.get_BottomMargin;
CDocumentSectionProps.prototype["put_BottomMargin"]   = CDocumentSectionProps.prototype.put_BottomMargin;
CDocumentSectionProps.prototype["get_HeaderDistance"] = CDocumentSectionProps.prototype.get_HeaderDistance;
CDocumentSectionProps.prototype["put_HeaderDistance"] = CDocumentSectionProps.prototype.put_HeaderDistance;
CDocumentSectionProps.prototype["get_FooterDistance"] = CDocumentSectionProps.prototype.get_FooterDistance;
CDocumentSectionProps.prototype["put_FooterDistance"] = CDocumentSectionProps.prototype.put_FooterDistance;