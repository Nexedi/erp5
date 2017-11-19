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
var History = AscCommon.History;

/**
 *
 * @constructor
 * @extends {CParagraphContentWithParagraphLikeContent}
 */
function ParaHyperlink()
{
	CParagraphContentWithParagraphLikeContent.call(this);

    this.Id = AscCommon.g_oIdCounter.Get_NewId();

    this.Type    = para_Hyperlink;
    this.Value   = "";
    this.Visited = false;
    this.ToolTip = "";

    // Добавляем данный класс в таблицу Id (обязательно в конце конструктора)
    AscCommon.g_oTableId.Add( this, this.Id );
}

ParaHyperlink.prototype = Object.create(CParagraphContentWithParagraphLikeContent.prototype);
ParaHyperlink.prototype.constructor = ParaHyperlink;

ParaHyperlink.prototype.Get_Id = function()
{
    return this.Id;
};


ParaHyperlink.prototype.Get_FirstTextPr2 = function()
{
    for(var i = 0; i < this.Content.length; ++i)
    {
        if(this.Content[i].Type === para_Run && !this.Content[i].Is_Empty())
        {
            return this.Content[i].Get_CompiledPr();
        }
    }
    return null;
};

ParaHyperlink.prototype.Copy = function(Selected)
{
    var NewHyperlink = CParagraphContentWithParagraphLikeContent.prototype.Copy.apply(this, arguments);
    NewHyperlink.Set_Value(this.Value);
    NewHyperlink.Set_ToolTip(this.ToolTip);
    NewHyperlink.Visited = this.Visited;
    return NewHyperlink;
};

ParaHyperlink.prototype.GetSelectedElementsInfo = function(Info, ContentPos, Depth)
{
    Info.Set_Hyperlink(this);
    CParagraphContentWithParagraphLikeContent.prototype.GetSelectedElementsInfo.apply(this, arguments);
};

ParaHyperlink.prototype.Add_ToContent = function(Pos, Item, UpdatePosition)
{
    if (para_Hyperlink === Item.Type)
    {
        // При добавлении гиперссылки в гиперссылку мы добавляем контент гиперссылки, а не ее целиком
        for (var ItemPos = 0, Count = Item.Content.length; ItemPos < Count; ItemPos++)
        {
            this.Add_ToContent(Pos + ItemPos, Item.Content[ItemPos], UpdatePosition);
        }

        return;
    }

	History.Add(new CChangesHyperlinkAddItem(this, Pos, [Item]));

    CParagraphContentWithParagraphLikeContent.prototype.Add_ToContent.apply(this, arguments);
};

ParaHyperlink.prototype.Remove_FromContent = function(Pos, Count, UpdatePosition)
{
    // Получим массив удаляемых элементов
    var DeletedItems = this.Content.slice( Pos, Pos + Count );
    History.Add(new CChangesHyperlinkRemoveItem(this, Pos, DeletedItems));

    CParagraphContentWithParagraphLikeContent.prototype.Remove_FromContent.apply(this, arguments);
};

ParaHyperlink.prototype.Add = function(Item)
{
	if (para_Hyperlink === Item.Type)
	{
		// Вместо добавления самого элемента добавляем его содержимое
		var Count = Item.Content.length;

		if (Count > 0)
		{
			var CurPos  = this.State.ContentPos;
			var CurItem = this.Content[CurPos];

			var CurContentPos = new CParagraphContentPos();
			CurItem.Get_ParaContentPos(false, false, CurContentPos);

			var NewItem = CurItem.Split(CurContentPos, 0);
			for (var Index = 0; Index < Count; Index++)
			{
				this.Add_ToContent(CurPos + Index + 1, Item.Content[Index], false);
			}
			this.Add_ToContent(CurPos + Count + 1, NewItem, false);
			this.State.ContentPos = CurPos + Count;
			this.Content[this.State.ContentPos].MoveCursorToEndPos();
		}
	}
	else
	{
		CParagraphContentWithParagraphLikeContent.prototype.Add.apply(this, arguments);
	}
};

ParaHyperlink.prototype.Clear_TextPr = function()
{
    var HyperlinkStyle = null;
    if ( undefined !== this.Paragraph && null !== this.Paragraph )
    {
        var Styles = this.Paragraph.Parent.Get_Styles();
        HyperlinkStyle = Styles.Get_Default_Hyperlink();
    }

    var Count = this.Content.length;
    for ( var Index = 0; Index < Count; Index++ )
    {
        var Item = this.Content[Index];
        Item.Clear_TextPr();

        if ( para_Run === Item.Type && null !== HyperlinkStyle )
            Item.Set_RStyle( HyperlinkStyle );
    }
};

ParaHyperlink.prototype.Clear_TextFormatting = function( DefHyper )
{
    var Count = this.Content.length;

    for (var Pos = 0; Pos < Count; Pos++)
    {
        var Item = this.Content[Pos];
        Item.Clear_TextFormatting(DefHyper);

        if (para_Run === Item.Type && null !== DefHyper && undefined !== DefHyper)
            Item.Set_RStyle(DefHyper);
    }
};

ParaHyperlink.prototype.Split = function (ContentPos, Depth)
{
    var NewHyperlink = CParagraphContentWithParagraphLikeContent.prototype.Split.apply(this, arguments);
    NewHyperlink.Set_Value(this.Value);
    NewHyperlink.Set_ToolTip(this.ToolTip);
    return NewHyperlink;
};

ParaHyperlink.prototype.CopyContent = function(Selected)
{
    var Content = CParagraphContentWithParagraphLikeContent.prototype.CopyContent.apply(this, arguments);

    for (var CurPos = 0, Count = Content.length; CurPos < Count; CurPos++)
    {
        var Item = Content[CurPos];
        Item.Clear_TextFormatting();
    }

    return Content;
};

//-----------------------------------------------------------------------------------
// Функции отрисовки
//-----------------------------------------------------------------------------------
ParaHyperlink.prototype.Draw_Elements = function(PDSE)
{
    PDSE.VisitedHyperlink = this.Visited;
    PDSE.Hyperlink = true;
    CParagraphContentWithParagraphLikeContent.prototype.Draw_Elements.apply(this, arguments);
    PDSE.VisitedHyperlink = false;
    PDSE.Hyperlink = false;
};

ParaHyperlink.prototype.Draw_Lines = function(PDSL)
{
    PDSL.VisitedHyperlink = this.Visited;
    PDSL.Hyperlink = true;
    CParagraphContentWithParagraphLikeContent.prototype.Draw_Lines.apply(this, arguments);
    PDSL.VisitedHyperlink = false;
    PDSL.Hyperlink = false;
};
//-----------------------------------------------------------------------------------
// Работаем со значениями
//-----------------------------------------------------------------------------------
ParaHyperlink.prototype.Set_Visited = function(Value)
{
    this.Visited = Value;
};

ParaHyperlink.prototype.Get_Visited = function()
{
    return this.Visited;
};

ParaHyperlink.prototype.Set_ToolTip = function(ToolTip)
{
    History.Add(new CChangesHyperlinkToolTip(this, this.ToolTip, ToolTip));
    this.ToolTip = ToolTip;
};

ParaHyperlink.prototype.Get_ToolTip = function()
{
    if ( null === this.ToolTip )
    {
        if ( "string" === typeof(this.Value) )
            return this.Value;
        else
            return "";
    }
    else
        return this.ToolTip;
};

ParaHyperlink.prototype.Get_Value = function()
{
    return this.Value;
};

ParaHyperlink.prototype.Set_Value = function(Value)
{
    History.Add(new CChangesHyperlinkValue(this, this.Value, Value));
    this.Value = Value;
};
//----------------------------------------------------------------------------------------------------------------------
// Функции совместного редактирования
//----------------------------------------------------------------------------------------------------------------------
ParaHyperlink.prototype.Write_ToBinary2 = function(Writer)
{
    Writer.WriteLong( AscDFH.historyitem_type_Hyperlink );

    // String : Id
    // String : Value
    // String : ToolTip
    // Long   : Количество элементов
    // Array of Strings : массив с Id элементов

    Writer.WriteString2( this.Id );
    if(!(editor && editor.isDocumentEditor))
    {
        this.Write_ToBinary2SpreadSheets(Writer);
        return;
    }

    Writer.WriteString2( this.Value );
    Writer.WriteString2( this.ToolTip );

    var Count = this.Content.length;
    Writer.WriteLong( Count );

    for ( var Index = 0; Index < Count; Index++ )
    {
        Writer.WriteString2( this.Content[Index].Get_Id() );
    }
};

ParaHyperlink.prototype.Read_FromBinary2 = function(Reader)
{
    // String : Id
    // String : Value
    // String : ToolTip
    // Long   : Количество элементов
    // Array of Strings : массив с Id элементов

    this.Id      = Reader.GetString2();
    this.Value   = Reader.GetString2();
    this.ToolTip = Reader.GetString2();

    var Count = Reader.GetLong();
    this.Content = [];

    for ( var Index = 0; Index < Count; Index++ )
    {
        var Element = AscCommon.g_oTableId.Get_ById( Reader.GetString2() );
        if ( null !== Element )
            this.Content.push( Element );
    }
};

ParaHyperlink.prototype.Write_ToBinary2SpreadSheets = function(Writer)
{
    Writer.WriteString2("");
    Writer.WriteString2("");
    Writer.WriteLong(0);
};

ParaHyperlink.prototype.Document_UpdateInterfaceState = function()
{
    var HyperText = new CParagraphGetText();
    this.Get_Text( HyperText );

    var HyperProps = new Asc.CHyperlinkProperty(this);
    HyperProps.put_Text( HyperText.Text );

    editor.sync_HyperlinkPropCallback(HyperProps);

    CParagraphContentWithParagraphLikeContent.prototype.Document_UpdateInterfaceState.apply(this, arguments);
};

function CParaHyperLinkStartState(HyperLink)
{
    this.Value = HyperLink.Value;
    this.ToolTip = HyperLink.ToolTip;
    this.Content = [];
    for(var i = 0; i < HyperLink.Content.length; ++i)
    {
        this.Content.push(HyperLink.Content);
    }
}

//--------------------------------------------------------export----------------------------------------------------
window['AscCommonWord'] = window['AscCommonWord'] || {};
window['AscCommonWord'].ParaHyperlink = ParaHyperlink;
