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

//     SectPr  : Настройки секци (размеры, поля)
//               PgSz : размеры страницы
//                     W, H, Orient
//               PgMar: отступы страницы
//                      Top, Left, Right, Bottom, Header, Footer
//

// Import
var g_oTableId = AscCommon.g_oTableId;
var History = AscCommon.History;

var section_borders_DisplayAllPages     = 0x00;
var section_borders_DisplayFirstPage    = 0x01;
var section_borders_DisplayNotFirstPage = 0x02;

var section_borders_OffsetFromPage = 0x00;
var section_borders_OffsetFromText = 0x01;

var section_borders_ZOrderBack  = 0x00;
var section_borders_ZOrderFront = 0x01;

function CSectionPr(LogicDocument)
{
    this.Id = AscCommon.g_oIdCounter.Get_NewId();

    this.Type          = 'undefined' !== typeof c_oAscSectionBreakType ? c_oAscSectionBreakType.NextPage : undefined;
    this.PageSize      = new CSectionPageSize();
    this.PageMargins   = new CSectionPageMargins();

    this.LogicDocument = LogicDocument;

    this.Borders       = new CSectionBorders();
    this.PageNumType   = new CSectionPageNumType();
    
    this.FooterFirst   = null;
    this.FooterEven    = null;
    this.FooterDefault = null;
    
    this.HeaderFirst   = null;
    this.HeaderEven    = null;
    this.HeaderDefault = null;
    
    this.TitlePage     = false;
    
    this.Columns       = new CSectionColumns(this);
       

    // Добавляем данный класс в таблицу Id (обязательно в конце конструктора)
    g_oTableId.Add( this, this.Id );
}

CSectionPr.prototype =
{
    Get_Id : function()
    {
        return this.Id;
    },

    Copy : function(Other, CopyHdrFtr)
    {
        if (!Other)
            return;

        // Тип
        this.Set_Type( Other.Type );

        // Настройки страницы
        this.Set_PageSize( Other.PageSize.W, Other.PageSize.H );
        this.Set_Orientation( Other.PageSize.Orient, false );

        // Настройки отступов
        this.Set_PageMargins( Other.PageMargins.Left, Other.PageMargins.Top, Other.PageMargins.Right, Other.PageMargins.Bottom );

        // Настройки границ
        this.Set_Borders_Left( Other.Borders.Left );
        this.Set_Borders_Top( Other.Borders.Top );
        this.Set_Borders_Right( Other.Borders.Right );
        this.Set_Borders_Bottom( Other.Borders.Bottom );
        this.Set_Borders_Display( Other.Borders.Display );
        this.Set_Borders_OffsetFrom( Other.Borders.OffsetFrom );
        this.Set_Borders_ZOrder( Other.Borders.ZOrder );

        // Колонтитулы
        if (true === CopyHdrFtr)
        {
            if (Other.HeaderFirst)
                this.Set_Header_First(Other.HeaderFirst.Copy());
            else
                this.Set_Header_First(null);

            if (Other.HeaderEven)
                this.Set_Header_Even(Other.HeaderEven.Copy());
            else
                this.Set_Header_Even(null);

            if (Other.HeaderDefault)
                this.Set_Header_Default(Other.HeaderDefault.Copy());
            else
                this.Set_Header_Default(null);

            if (Other.FooterFirst)
                this.Set_Footer_First(Other.FooterFirst.Copy());
            else
                this.Set_Footer_First(null);

            if (Other.FooterEven)
                this.Set_Footer_Even(Other.FooterEven.Copy());
            else
                this.Set_Footer_Even(null);

            if (Other.FooterDefault)
                this.Set_Footer_Default(Other.FooterDefault.Copy());
            else
                this.Set_Footer_Default(null);
        }
        else
        {
            this.Set_Header_First(Other.HeaderFirst);
            this.Set_Header_Even(Other.HeaderEven);
            this.Set_Header_Default(Other.HeaderDefault);
            this.Set_Footer_First(Other.FooterFirst);
            this.Set_Footer_Even(Other.FooterEven);
            this.Set_Footer_Default(Other.FooterDefault);
        }

        this.Set_PageNum_Start( Other.PageNumType.Start );

        this.Set_Columns_EqualWidth(Other.Columns.EqualWidth);
        this.Set_Columns_Num(Other.Columns.Num);
        this.Set_Columns_Sep(Other.Columns.Sep);
        this.Set_Columns_Space(Other.Columns.Space);
        for (var ColumnIndex = 0, ColumnsCount = Other.Columns.Cols.length; ColumnIndex < ColumnsCount; ++ColumnIndex)
        {
            var Column = Other.Columns.Cols[ColumnIndex];
            this.Set_Columns_Col(ColumnIndex, Column.W, Column.Space);
        }
    },
    
    Clear_AllHdrFtr : function()
    {
        this.Set_Header_First(null);
        this.Set_Header_Even(null);
        this.Set_Header_Default(null);
        this.Set_Footer_First(null);
        this.Set_Footer_Even(null);
        this.Set_Footer_Default(null);
    },

    Is_AllHdrFtrNull : function()
    {
        if (null !== this.FooterFirst
            || null !== this.HeaderFirst
            || null !== this.FooterDefault
            || null !== this.HeaderDefault
            || null !== this.FooterEven
            || null !== this.HeaderEven)
            return false;

        return true;
    },

    Get_AllHdrFtrs : function(HdrFtrs)
    {
        if (!HdrFtrs)
            HdrFtrs = [];

        if (null !== this.HeaderFirst) HdrFtrs.push(this.HeaderFirst);
        if (null !== this.HeaderEven) HdrFtrs.push(this.HeaderEven);
        if (null !== this.HeaderDefault) HdrFtrs.push(this.HeaderDefault);

        if (null !== this.FooterFirst) HdrFtrs.push(this.FooterFirst);
        if (null !== this.FooterEven) HdrFtrs.push(this.FooterEven);
        if (null !== this.FooterDefault) HdrFtrs.push(this.FooterDefault);

        return HdrFtrs;
    },

    Compare_PageSize : function(OtherSectionPr)
    {
        var ThisPS = this.PageSize;
        var OtherPS = OtherSectionPr.PageSize;

        if ( Math.abs( ThisPS.W - OtherPS.W ) > 0.001 || Math.abs( ThisPS.H - OtherPS.H ) > 0.001 || ThisPS.Orient !== OtherPS.Orient )
            return false;

        return true;
    },

    Set_Type : function(Type)
    {
        if ( this.Type !== Type )
        {
            History.Add(this, { Type: AscDFH.historyitem_Section_Type, Old: this.Type, New: Type });
            this.Type = Type;
        }
    },

    Get_Type : function()
    {
        return this.Type;
    },

    Set_PageSize : function(W, H)
    {
        if ( Math.abs( W - this.PageSize.W ) > 0.001 || Math.abs( H - this.PageSize.H ) > 0.001 )
        {
            History.Add(this, { Type: AscDFH.historyitem_Section_PageSize_Size, Old: { W : this.PageSize.W, H : this.PageSize.H }, New: { W : W, H : H } });

            H = Math.max(2.6, H);
            W = Math.max(12.7, W);

            this.PageSize.W = W;
            this.PageSize.H = H;
        }
    },

    Get_PageWidth : function()
    {
        return this.PageSize.W;
    },

    Get_PageHeight : function()
    {
        return this.PageSize.H;
    },

    Set_PageMargins : function(_L, _T, _R, _B)
    {
        // Значения могут прийти как undefined, в этом случае мы поля со значением undefined не меняем
        var L = ( undefined !== _L ? _L : this.PageMargins.Left );
        var T = ( undefined !== _T ? _T : this.PageMargins.Top );
        var R = ( undefined !== _R ? _R : this.PageMargins.Right );
        var B = ( undefined !== _B ? _B : this.PageMargins.Bottom );

        if ( Math.abs( L - this.PageMargins.Left ) > 0.001 || Math.abs( T - this.PageMargins.Top ) > 0.001 || Math.abs( R - this.PageMargins.Right ) > 0.001 || Math.abs( B - this.PageMargins.Bottom ) > 0.001 )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_PageMargins, Old : { L : this.PageMargins.Left, T : this.PageMargins.Top, R : this.PageMargins.Right, B : this.PageMargins.Bottom }, New : { L : L, T : T, R : R, B : B }  } );

            this.PageMargins.Left   = L;
            this.PageMargins.Top    = T;
            this.PageMargins.Right  = R;
            this.PageMargins.Bottom = B;
        }
    },

    Get_PageMargin_Left : function()
    {
        return this.PageMargins.Left;
    },

    Get_PageMargin_Right : function()
    {
        return this.PageMargins.Right;
    },

    Get_PageMargin_Top : function()
    {
        return this.PageMargins.Top;
    },

    Get_PageMargin_Bottom : function()
    {
        return this.PageMargins.Bottom;
    },

    Set_Orientation : function(Orient, ApplySize)    
    {
        if ( this.PageSize.Orient !== Orient )
        {            
            History.Add(this, { Type: AscDFH.historyitem_Section_PageSize_Orient, Old: this.PageSize.Orient, New: Orient });
            this.PageSize.Orient = Orient;
            
            if ( true === ApplySize )
            {
                // При смене ориентации меняем местами высоту и ширину страницы и изменяем отступы

                var W = this.PageSize.W;
                var H = this.PageSize.H;

                var L = this.PageMargins.Left;
                var R = this.PageMargins.Right;
                var T = this.PageMargins.Top;
                var B = this.PageMargins.Bottom;
                
                this.Set_PageSize(H, W);
                
                if ( Asc.c_oAscPageOrientation.PagePortrait === Orient )
                    this.Set_PageMargins( T, R, B, L );
                else
                    this.Set_PageMargins( B, L, T, R );
            }
        }
    },

    Get_Orientation : function()
    {
        return this.PageSize.Orient;
    },

    Set_Borders_Left : function(Border)
    {
        if ( true !== this.Borders.Left.Compare( Border ) )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_Borders_Left, Old : this.Borders.Left, New : Border } );
            this.Borders.Left = Border;
        }
    },

    Get_Borders_Left : function()
    {
        return this.Borders.Left;
    },

    Set_Borders_Top : function(Border)
    {
        if ( true !== this.Borders.Top.Compare( Border ) )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_Borders_Top, Old : this.Borders.Top, New : Border } );
            this.Borders.Top = Border;
        }
    },

    Get_Borders_Top : function()
    {
        return this.Borders.Top;
    },

    Set_Borders_Right : function(Border)
    {
        if ( true !== this.Borders.Right.Compare( Border ) )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_Borders_Right, Old : this.Borders.Right, New : Border } );
            this.Borders.Right = Border;
        }
    },

    Get_Borders_Right : function()
    {
        return this.Borders.Right;
    },

    Set_Borders_Bottom : function(Border)
    {
        if ( true !== this.Borders.Bottom.Compare( Border ) )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_Borders_Bottom, Old : this.Borders.Bottom, New : Border } );
            this.Borders.Bottom = Border;
        }
    },

    Get_Borders_Bottom : function()
    {
        return this.Borders.Bottom;
    },

    Set_Borders_Display : function(Display)
    {
        if ( Display !== this.Borders.Display )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_Borders_Display, Old : this.Borders.Display, New : Display } );
            this.Borders.Display = Display;
        }
    },

    Get_Borders_Display : function()
    {
        return this.Borders.Display;
    },

    Set_Borders_OffsetFrom : function(OffsetFrom)
    {
        if ( OffsetFrom !== this.Borders.OffsetFrom )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_Borders_OffsetFrom, Old : this.Borders.OffsetFrom, New : OffsetFrom } );
            this.Borders.OffsetFrom = OffsetFrom;
        }
    },

    Get_Borders_OffsetFrom : function()
    {
        return this.Borders.OffsetFrom;
    },

    Set_Borders_ZOrder : function(ZOrder)
    {
        if ( ZOrder !== this.Borders.ZOrder )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_Borders_ZOrder, Old : this.Borders.ZOrder, New : ZOrder } );
            this.Borders.ZOrder = ZOrder;
        }
    },

    Get_Borders_ZOrder : function()
    {
        return this.Borders.ZOrder;
    },
    
    Set_Footer_First : function(Footer)
    {
        if ( Footer !== this.FooterFirst )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_Footer_First, Old : this.FooterFirst, New : Footer } );
            this.FooterFirst = Footer;
        }
    },
    
    Get_Footer_First : function()
    {
        return this.FooterFirst;
    },

    Set_Footer_Even : function(Footer)
    {
        if ( Footer !== this.FooterEven )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_Footer_Even, Old : this.FooterEven, New : Footer } );
            this.FooterEven = Footer;
        }
    },

    Get_Footer_Even : function()
    {
        return this.FooterEven;
    },

    Set_Footer_Default : function(Footer)
    {
        if ( Footer !== this.FooterDefault )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_Footer_Default, Old : this.FooterDefault, New : Footer } );
            this.FooterDefault = Footer;
        }
    },

    Get_Footer_Default : function()
    {
        return this.FooterDefault;
    },

    Set_Header_First : function(Header)
    {
        if ( Header !== this.HeaderFirst )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_Header_First, Old : this.HeaderFirst, New : Header } );
            this.HeaderFirst = Header;
        }
    },

    Get_Header_First : function()
    {
        return this.HeaderFirst;
    },

    Set_Header_Even : function(Header)
    {
        if ( Header !== this.HeaderEven )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_Header_Even, Old : this.HeaderEven, New : Header } );
            this.HeaderEven = Header;
        }
    },

    Get_Header_Even : function()
    {
        return this.HeaderEven;
    },

    Set_Header_Default : function(Header)
    {
        if ( Header !== this.HeaderDefault )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_Header_Default, Old : this.HeaderDefault, New : Header } );
            this.HeaderDefault = Header;
        }
    },

    Get_Header_Default : function()
    {
        return this.HeaderDefault;
    },
    
    Set_TitlePage : function(Value)
    {
        if ( Value !== this.TitlePage )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_TitlePage, Old : this.TitlePage, New : Value } );
            this.TitlePage = Value;
        }
    },
    
    Get_TitlePage : function()
    {
        return this.TitlePage;
    },
    
    Set_PageMargins_Header : function(Header)
    {
        if ( Header !== this.PageMargins.Header )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_PageMargins_Header, Old : this.PageMargins.Header, New : Header } );
            this.PageMargins.Header = Header;
        }
    },
    
    Get_PageMargins_Header : function()
    {
        return this.PageMargins.Header;
    },

    Set_PageMargins_Footer : function(Footer)
    {
        if ( Footer !== this.PageMargins.Footer )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_PageMargins_Footer, Old : this.PageMargins.Footer, New : Footer } );
            this.PageMargins.Footer = Footer;
        }
    },

    Get_PageMargins_Footer : function()
    {
        return this.PageMargins.Footer;
    },
    
    Get_HdrFtr : function(bHeader, bFirst, bEven)
    {
        if ( true === bHeader )
        {
            if ( true === bFirst )
                return this.HeaderFirst;
            else if ( true === bEven )
                return this.HeaderEven;
            else
                return this.HeaderDefault;
        }
        else
        {
            if ( true === bFirst )
                return this.FooterFirst;
            else if ( true === bEven )
                return this.FooterEven;
            else
                return this.FooterDefault;
        }
    },
    
    Set_HdrFtr : function(bHeader, bFirst, bEven, HdrFtr)
    {
        if ( true === bHeader )
        {
            if ( true === bFirst )
                return this.Set_Header_First( HdrFtr );
            else if ( true === bEven )
                return this.Set_Header_Even( HdrFtr );
            else
                return this.Set_Header_Default( HdrFtr );
        }
        else
        {
            if ( true === bFirst )
                return this.Set_Footer_First( HdrFtr );
            else if ( true === bEven )
                return this.Set_Footer_Even( HdrFtr );
            else
                return this.Set_Footer_Default( HdrFtr );
        }
    },
    
    Get_HdrFtrInfo : function(HdrFtr)
    {
        if  ( HdrFtr === this.HeaderFirst )
            return { Header : true, First : true, Even : false };
        else if ( HdrFtr === this.HeaderEven )
            return { Header : true, First : false, Even : true };
        else if ( HdrFtr === this.HeaderDefault )
            return { Header : true, First : false, Even : false };
        else if ( HdrFtr === this.FooterFirst )
            return { Header : false, First : true, Even : false };
        else if ( HdrFtr === this.FooterEven )
            return { Header : false, First : false, Even : true };
        else if ( HdrFtr === this.FooterDefault )
            return { Header : false, First : false, Even : false };

        return null;
    },
    
    Set_PageNum_Start : function(Start)
    {
        if ( Start !== this.PageNumType.Start )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_PageNumType_Start, Old : this.PageNumType.Start, New : Start } );
            this.PageNumType.Start = Start;
        }
    },
    
    Get_PageNum_Start : function()
    {
        return this.PageNumType.Start;
    },

    Get_ColumnsCount : function()
    {
        return this.Columns.Get_Count();
    },

    Get_ColumnWidth : function(ColIndex)
    {
        return this.Columns.Get_ColumnWidth(ColIndex);
    },

    Get_ColumnSpace : function(ColIndex)
    {
        return this.Columns.Get_ColumnSpace(ColIndex);
    },

    Set_Columns_EqualWidth : function(Equal)
    {
        if ( Equal !== this.Columns.Equal )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_Columns_EqualWidth, Old : this.Columns.EqualWidth, New : Equal } );
            this.Columns.EqualWidth = Equal;
        }
    },
    
    Set_Columns_Space : function(Space)
    {
        if ( Space !== this.Columns.Space )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_Columns_Space, Old : this.Columns.Space, New : Space } );
            this.Columns.Space = Space;
        }
    },
    
    Set_Columns_Num : function(_Num)
    {
        var Num = Math.max( _Num, 1 );
        
        if ( Num !== this.Columns.Num )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_Columns_Num, Old : this.Columns.Num, New : Num } );
            this.Columns.Num = Num;
        }
    },
    
    Set_Columns_Sep : function(Sep)
    {
        if ( Sep !== this.Columns.Sep )
        {
            History.Add( this, { Type : AscDFH.historyitem_Section_Columns_Sep, Old : this.Columns.Sep, New : Sep } );
            this.Columns.Sep = Sep;
        }
    },

    Set_Columns_Cols : function(Cols)
    {
        History.Add(this, {Type : AscDFH.historyitem_Section_Columns_SetCols, Old : this.Columns.Cols, New : Cols});
        this.Columns.Cols = Cols;
    },

    Set_Columns_Col : function(Index, W, Space)
    {
        var OldCol = this.Columns.Cols[Index];
        
        if ( undefined === OldCol || OldCol.Space !== Space || OldCol.W !== W )
        {
            var NewCol = new CSectionColumn();
            NewCol.W     = W;
            NewCol.Space = Space;
            
            History.Add( this, { Type : AscDFH.historyitem_Section_Columns_Col, Index : Index, Old : OldCol, New : NewCol } );
            this.Columns.Cols[Index] = NewCol;
        }
    },   
    
    Get_LayoutInfo : function()
    {
        // Получаем информацию о колонках в данной секции
        
        var Margins = this.PageMargins;
        var H       = this.PageSize.H;
        var _W      = this.PageSize.W;
        var W       = _W - Margins.Left - Margins.Right;
        
        // Если так случилось, что правое и левое поля в сумме больше ширины, тогда оставляем для документа 1 см ширины.
        if ( W < 0 )
            W = 10;
        
        var Columns = this.Columns;
        
        var Layout = new CSectionLayoutInfo(Margins.Left, Margins.Top, _W - Margins.Right, H - Margins.Bottom);
        var ColumnsInfo = Layout.Columns;
        
        if ( true === Columns.EqualWidth )
        {
            var Num   = Math.max( Columns.Num, 1 );
            var Space = Columns.Space;
            
            var ColW  = (W - Space * ( Num - 1 )) / Num;
            
            // Если так случилось, что под колонки места не осталось, тогда делаем колонки шириной 0.3 мм, оставшееся 
            // свободное место распределяем под Space, но если и оставшегося места не осталось, тогда Space делаем 0, а
            // колонки пусть выходят за пределы W.
            if ( ColW < 0 )
            {
                ColW = 0.3;
                
                var __W = W - ColW * Num;
                
                if ( _W > 0 && Num > 1 )
                    Space = _W / ( Num - 1 );
                else
                    Space = 0;
            }
            
            var X = Margins.Left;
            for ( var Pos = 0; Pos < Num; Pos++ )
            {
                var X0 = X;
                var X1 = X + ColW;
                
                ColumnsInfo.push( new CSectionLayoutColumnInfo(X0, X1) );
                
                X += ColW + Space;
            }
        }
        else
        {
            var Num = Columns.Cols.length;
            
            // Когда задаются колонки не равномерно, то Word плюет на поля, заданные в документа и ориентируется только
            // по размеру колонок дальше. (если ни 1 колонка не задана, тогда Word добавляет 1 колонку шириной 17.09 см)
            
            if ( Num <= 0 )
            {
                ColumnsInfo.push( new CSectionLayoutColumnInfo(Margins.Left, Margins.Left + 170.9) );
            }
            else
            {
                var X = Margins.Left;
                for ( var Pos = 0; Pos < Num; Pos++ )
                {
                    var Col = this.Columns.Cols[Pos];
                    var X0 = X;
                    var X1 = X + Col.W;

                    ColumnsInfo.push( new CSectionLayoutColumnInfo(X0, X1) );
                    
                    X += Col.W + Col.Space;
                }
            }
        }       
        
        return Layout;
    },
//----------------------------------------------------------------------------------------------------------------------
// Undo/Redo функции
//----------------------------------------------------------------------------------------------------------------------
    Undo : function(Data)
    {
        var Type = Data.Type;

        switch (Type)
        {
            case AscDFH.historyitem_Section_PageSize_Orient :
            {
                this.PageSize.Orient = Data.Old;

                break;
            }

            case  AscDFH.historyitem_Section_PageSize_Size:
            {
                this.PageSize.W = Data.Old.W;
                this.PageSize.H = Data.Old.H;

                break;
            }

            case AscDFH.historyitem_Section_PageMargins:
            {
                this.PageMargins.Left   = Data.Old.L;
                this.PageMargins.Top    = Data.Old.T;
                this.PageMargins.Right  = Data.Old.R;
                this.PageMargins.Bottom = Data.Old.B;

                break;
            }

            case AscDFH.historyitem_Section_Type:
            {
                this.Type = Data.Old;

                break;
            }

            case AscDFH.historyitem_Section_Borders_Left:
            {
                this.Borders.Left = Data.Old;
                break;
            }

            case AscDFH.historyitem_Section_Borders_Top:
            {
                this.Borders.Top = Data.Old;
                break;
            }

            case AscDFH.historyitem_Section_Borders_Right:
            {
                this.Borders.Right = Data.Old;
                break;
            }

            case AscDFH.historyitem_Section_Borders_Bottom:
            {
                this.Borders.Bottom = Data.Old;
                break;
            }

            case AscDFH.historyitem_Section_Borders_Display:
            {
                this.Borders.Display = Data.Old;
                break;
            }

            case AscDFH.historyitem_Section_Borders_OffsetFrom:
            {
                this.Borders.OffsetFrom = Data.Old;
                break;
            }

            case AscDFH.historyitem_Section_Borders_ZOrder:
            {
                this.Borders.ZOrder = Data.Old;
                break;
            }
                
            case AscDFH.historyitem_Section_Header_First:
            {
                this.HeaderFirst = Data.Old;
                break;
            }

            case AscDFH.historyitem_Section_Header_Even:
            {
                this.HeaderEven = Data.Old;
                break;
            }

            case AscDFH.historyitem_Section_Header_Default:
            {
                this.HeaderDefault = Data.Old;
                break;
            }

            case AscDFH.historyitem_Section_Footer_First:
            {
                this.FooterFirst = Data.Old;
                break;
            }

            case AscDFH.historyitem_Section_Footer_Even:
            {
                this.FooterEven = Data.Old;
                break;
            }

            case AscDFH.historyitem_Section_Footer_Default:
            {
                this.FooterDefault = Data.Old;
                break;
            }

            case AscDFH.historyitem_Section_TitlePage:
            {
                this.TitlePage = Data.Old;
                break;
            }
                
            case AscDFH.historyitem_Section_PageMargins_Header:
            {
                this.PageMargins.Header = Data.Old;
                break;
            }
                
            case AscDFH.historyitem_Section_PageMargins_Footer:
            {
                this.PageMargins.Footer = Data.Old;
                break;
            }
                
            case AscDFH.historyitem_Section_PageNumType_Start:
            {
                this.PageNumType.Start = Data.Old;
                break;
            }
                
            case AscDFH.historyitem_Section_Columns_EqualWidth:
            {
                this.Columns.EqualWidth = Data.Old;
                break;
            }
                
            case AscDFH.historyitem_Section_Columns_Space:
            {
                this.Columns.Space = Data.Old;
                break;
            }
                
            case AscDFH.historyitem_Section_Columns_Num:
            {
                this.Columns.Num = Data.Old;
                break;
            }
                
            case AscDFH.historyitem_Section_Columns_Sep:
            {
                this.Columns.Sep = Data.Old;
                break;
            }
                
            case AscDFH.historyitem_Section_Columns_Col:
            {
                this.Columns.Cols[Data.Index] = Data.Old;
                break;
            }

            case AscDFH.historyitem_Section_Columns_SetCols:
            {
                this.Columns.Cols = Data.Old;
                break;
            }
        }
    },

    Redo : function(Data)
    {
        var Type = Data.Type;

        switch (Type)
        {
            case AscDFH.historyitem_Section_PageSize_Orient :
            {
                this.PageSize.Orient = Data.New;

                break;
            }

            case  AscDFH.historyitem_Section_PageSize_Size:
            {
                this.PageSize.W = Data.New.W;
                this.PageSize.H = Data.New.H;

                break;
            }

            case AscDFH.historyitem_Section_PageMargins:
            {
                this.PageMargins.Left   = Data.New.L;
                this.PageMargins.Top    = Data.New.T;
                this.PageMargins.Right  = Data.New.R;
                this.PageMargins.Bottom = Data.New.B;

                break;
            }

            case AscDFH.historyitem_Section_Type:
            {
                this.Type = Data.New;

                break;
            }

            case AscDFH.historyitem_Section_Borders_Left:
            {
                this.Borders.Left = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_Borders_Top:
            {
                this.Borders.Top = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_Borders_Right:
            {
                this.Borders.Right = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_Borders_Bottom:
            {
                this.Borders.Bottom = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_Borders_Display:
            {
                this.Borders.Display = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_Borders_OffsetFrom:
            {
                this.Borders.OffsetFrom = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_Borders_ZOrder:
            {
                this.Borders.ZOrder = Data.New;
                break;
            }
                
            case AscDFH.historyitem_Section_Header_First:
            {
                this.HeaderFirst = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_Header_Even:
            {
                this.HeaderEven = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_Header_Default:
            {
                this.HeaderDefault = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_Footer_First:
            {
                this.FooterFirst = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_Footer_Even:
            {
                this.FooterEven = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_Footer_Default:
            {
                this.FooterDefault = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_TitlePage:
            {
                this.TitlePage = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_PageMargins_Header:
            {
                this.PageMargins.Header = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_PageMargins_Footer:
            {
                this.PageMargins.Footer = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_PageNumType_Start:
            {
                this.PageNumType.Start = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_Columns_EqualWidth:
            {
                this.Columns.EqualWidth = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_Columns_Space:
            {
                this.Columns.Space = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_Columns_Num:
            {
                this.Columns.Num = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_Columns_Sep:
            {
                this.Columns.Sep = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_Columns_Col:
            {
                this.Columns.Cols[Data.Index] = Data.New;
                break;
            }

            case AscDFH.historyitem_Section_Columns_SetCols:
            {
                this.Columns.Cols = Data.New;
                break;
            }
        }
    },

    Refresh_RecalcData : function(Data)
    {
        // Найдем данную секцию в документе
        var Index = this.LogicDocument.SectionsInfo.Find( this );

        if ( -1 === Index )
            return;

        // Здесь есть 1 исключение: когда мы добавляем колонтитул для первой страницы, может так получиться, что 
        // у данной секции флаг TitlePage = False, а значит пересчет надо запускать с места где данный колонтитул
        // первый раз начнет использоваться, а не с текущей секции.

        if ( (AscDFH.historyitem_Section_Header_First === Data.Type || AscDFH.historyitem_Section_Footer_First === Data.Type) && false === this.TitlePage )
        {
            var bHeader = AscDFH.historyitem_Section_Header_First === Data.Type ? true : false
            var SectionsCount = this.LogicDocument.SectionsInfo.Get_SectionsCount();
            while ( Index < SectionsCount - 1 )
            {
                Index++;

                var TempSectPr = this.LogicDocument.SectionsInfo.Get_SectPr2(Index).SectPr;

                // Если в следующей секции свой колонтитул, тогда наш добавленный колонтитул вообще ни на что не влияет
                if ( (true === bHeader && null !== TempSectPr.Get_Header_First()) || (true !== bHeader && null !== TempSectPr.Get_Footer_First()) )
                    break;

                // Если в следующей секции есть титульная страница, значит мы нашли нужную секцию
                if ( true === TempSectPr.Get_TitlePage() )
                {
                    if ( 0 === Index )
                    {
                        this.LogicDocument.Refresh_RecalcData2(0, 0);
                    }
                    else
                    {
                        var DocIndex = this.LogicDocument.SectionsInfo.Elements[Index - 1].Index + 1;
                        this.LogicDocument.Refresh_RecalcData2( DocIndex, 0 );
                    }
                }
            }
        }
        else
        {
            if ( 0 === Index )
            {
                // Первая секция, значит мы должны пересчитать начиная с самого начала документа
                this.LogicDocument.Refresh_RecalcData2(0, 0);
            }
            else
            {
                // Ищем номер элемента, на котором закончилась предыдущая секция, начиная со следующего после него элемента
                // и пересчитываем документ. 
                var DocIndex = this.LogicDocument.SectionsInfo.Elements[Index - 1].Index + 1;
                this.LogicDocument.Refresh_RecalcData2( DocIndex, 0 );
            }
        }
        
        // Дополнительно кроме этого мы должны обновить пересчет в колонтитулах, причем только начиная с данной секции
        this.LogicDocument.On_SectionChange( this );
    },
//----------------------------------------------------------------------------------------------------------------------
// Функции совместного редактирования
//----------------------------------------------------------------------------------------------------------------------
    Save_Changes : function(Data, Writer)
    {
        // Сохраняем изменения из тех, которые используются для Undo/Redo в бинарный файл.
        // Long : тип класса
        // Long : тип изменений

        Writer.WriteLong( AscDFH.historyitem_type_Section );

        var Type = Data.Type;

        // Пишем тип
        Writer.WriteLong( Type );

        switch ( Type )
        {
            case AscDFH.historyitem_Section_PageSize_Orient:
            {
                // Byte : Orient
                Writer.WriteByte( Data.New );

                break;
            }

            case  AscDFH.historyitem_Section_PageSize_Size:
            {
                // Double : W
                // Double : H
                Writer.WriteDouble(Data.New.W);
                Writer.WriteDouble(Data.New.H);

                break;
            }

            case AscDFH.historyitem_Section_PageMargins:
            {
                // Double : Left
                // Double : Top
                // Double : Right
                // Double : Bottom

                Writer.WriteDouble( Data.New.L );
                Writer.WriteDouble( Data.New.T );
                Writer.WriteDouble( Data.New.R );
                Writer.WriteDouble( Data.New.B );

                break;
            }

            case AscDFH.historyitem_Section_Type:
            {
                // Byte : Type
                Writer.WriteByte( Data.New );

                break;
            }

            case AscDFH.historyitem_Section_Borders_Left:
            case AscDFH.historyitem_Section_Borders_Top:
            case AscDFH.historyitem_Section_Borders_Right:
            case AscDFH.historyitem_Section_Borders_Bottom:
            {
                // Variable : CDocumentBorder
                Data.New.Write_ToBinary( Writer );
                break;
            }

            case AscDFH.historyitem_Section_Borders_Display:
            case AscDFH.historyitem_Section_Borders_OffsetFrom:
            case AscDFH.historyitem_Section_Borders_ZOrder:
            {
                // Byte : Value
                Writer.WriteByte( Data.New );
                break;
            }

            case AscDFH.historyitem_Section_Header_First:            
            case AscDFH.historyitem_Section_Header_Even:            
            case AscDFH.historyitem_Section_Header_Default:            
            case AscDFH.historyitem_Section_Footer_First:            
            case AscDFH.historyitem_Section_Footer_Even:            
            case AscDFH.historyitem_Section_Footer_Default:
            {
                // Bool : Is null
                // false ->
                //      String : Id колонтитула
                
                if ( null === Data.New )
                    Writer.WriteBool( true );
                else
                {
                    Writer.WriteBool( false );
                    Writer.WriteString2( Data.New.Get_Id() );
                }
                
                break;
            }
                
            case AscDFH.historyitem_Section_TitlePage:
            {
                // Bool : TitlePage
                
                Writer.WriteBool( Data.New );

                break;
            }

            case AscDFH.historyitem_Section_PageMargins_Header:
            case AscDFH.historyitem_Section_PageMargins_Footer:                
            {
                // Double : Header/Footer distance
                
                Writer.WriteDouble( Data.New );
                
                break;
            }

            case AscDFH.historyitem_Section_PageNumType_Start:
            {
                // Long : PageNumType.Start
                
                Writer.WriteLong( Data.New );
                break;
            }

            case AscDFH.historyitem_Section_Columns_EqualWidth:
            {
                // Bool : Equal
                Writer.WriteBool( Data.New );
                break;
            }

            case AscDFH.historyitem_Section_Columns_Space:
            {
                // Double : Space
                Writer.WriteDouble( Data.New );
                break;
            }

            case AscDFH.historyitem_Section_Columns_Num:
            {
                // Long : Num
                Writer.WriteLong( Data.New );
                break;
            }

            case AscDFH.historyitem_Section_Columns_Sep:
            {
                // Bool : Sep
                Writer.WriteBool( Data.New );
                break;
            }

            case AscDFH.historyitem_Section_Columns_Col:
            {
                // Long : Index
                // Bool : undefined ?
                // false -> 
                //   Variable : CSectionColumn
                
                Writer.WriteLong( Data.Index );
                if ( undefined === Data.New )
                    Writer.WriteBool( true );
                else
                {
                    Writer.WriteBool( false );
                    Data.New.Write_ToBinary( Writer );
                }

                break;
            }

            case AscDFH.historyitem_Section_Columns_SetCols:
            {
                // Long : Count
                // Array of variable : array of CSectionColumn

                var Count = Data.New.length;
                Writer.WriteLong(Count);
                for (var Index = 0; Index < Count; ++Index)
                {
                    Data.New[Index].Write_ToBinary(Writer);
                }
                break;
            }
        }

    },

    Load_Changes : function(Reader)
    {
        // Сохраняем изменения из тех, которые используются для Undo/Redo в бинарный файл.
        // Long : тип класса
        // Long : тип изменений

        var ClassType = Reader.GetLong();
        if ( AscDFH.historyitem_type_Section != ClassType )
            return;

        var Type = Reader.GetLong();

        switch ( Type )
        {
            case  AscDFH.historyitem_Section_PageSize_Orient:
            {
                // Byte : Orient
                this.PageSize.Orient = Reader.GetByte();

                break;
            }

            case  AscDFH.historyitem_Section_PageSize_Size:
            {
                // Double : W
                // Double : H
                this.PageSize.W = Reader.GetDouble();
                this.PageSize.H = Reader.GetDouble();

                break;
            }

            case AscDFH.historyitem_Section_PageMargins:
            {
                // Double : Left
                // Double : Top
                // Double : Right
                // Double : Bottom

                this.PageMargins.Left   = Reader.GetDouble();
                this.PageMargins.Top    = Reader.GetDouble();
                this.PageMargins.Right  = Reader.GetDouble();
                this.PageMargins.Bottom = Reader.GetDouble();

                break;
            }

            case AscDFH.historyitem_Section_Type:
            {
                // Byte : Type
                this.Type = Reader.GetByte();

                break;
            }

            case AscDFH.historyitem_Section_Borders_Left:
            {
                // Variable : CDocumentBorder
                this.Borders.Left.Read_FromBinary(Reader);
                break;
            }

            case AscDFH.historyitem_Section_Borders_Top:
            {
                // Variable : CDocumentBorder
                this.Borders.Top.Read_FromBinary(Reader);
                break;
            }

            case AscDFH.historyitem_Section_Borders_Right:
            {
                // Variable : CDocumentBorder
                this.Borders.Right.Read_FromBinary(Reader);
                break;
            }

            case AscDFH.historyitem_Section_Borders_Bottom:
            {
                // Variable : CDocumentBorder
                this.Borders.Bottom.Read_FromBinary(Reader);
                break;
            }

            case AscDFH.historyitem_Section_Borders_Display:
            {
                // Byte : Value
                this.Borders.Display = Reader.GetByte();
                break;
            }

            case AscDFH.historyitem_Section_Borders_OffsetFrom:
            {
                // Byte : Value
                this.Borders.OffsetFrom = Reader.GetByte();
                break;
            }

            case AscDFH.historyitem_Section_Borders_ZOrder:
            {
                // Byte : Value
                this.Borders.ZOrder = Reader.GetByte();
                break;
            }

            case AscDFH.historyitem_Section_Header_First:
            {
                // Bool : Is null
                // false ->
                //      String : Id колонтитула

                if ( true === Reader.GetBool() )
                    this.HeaderFirst = null;
                else
                    this.HeaderFirst = g_oTableId.Get_ById( Reader.GetString2() );

                break;
            }

            case AscDFH.historyitem_Section_Header_Even:
            {
                // Bool : Is null
                // false ->
                //      String : Id колонтитула

                if ( true === Reader.GetBool() )
                    this.HeaderEven = null;
                else
                    this.HeaderEven = g_oTableId.Get_ById( Reader.GetString2() );

                break;
            }

            case AscDFH.historyitem_Section_Header_Default:
            {
                // Bool : Is null
                // false ->
                //      String : Id колонтитула

                if ( true === Reader.GetBool() )
                    this.HeaderDefault = null;
                else
                    this.HeaderDefault = g_oTableId.Get_ById( Reader.GetString2() );

                break;
            }

            case AscDFH.historyitem_Section_Footer_First:
            {
                // Bool : Is null
                // false ->
                //      String : Id колонтитула

                if ( true === Reader.GetBool() )
                    this.FooterFirst = null;
                else
                    this.FooterFirst = g_oTableId.Get_ById( Reader.GetString2() );

                break;
            }

            case AscDFH.historyitem_Section_Footer_Even:
            {
                // Bool : Is null
                // false ->
                //      String : Id колонтитула

                if ( true === Reader.GetBool() )
                    this.FooterEven = null;
                else
                    this.FooterEven = g_oTableId.Get_ById( Reader.GetString2() );

                break;
            }

            case AscDFH.historyitem_Section_Footer_Default:
            {
                // Bool : Is null
                // false ->
                //      String : Id колонтитула

                if ( true === Reader.GetBool() )
                    this.FooterDefault = null;
                else
                    this.FooterDefault = g_oTableId.Get_ById( Reader.GetString2() );

                break;
            }

            case AscDFH.historyitem_Section_TitlePage:
            {
                // Bool : TitlePage

                this.TitlePage = Reader.GetBool();

                break;
            }

            case AscDFH.historyitem_Section_PageMargins_Header:
            {
                // Double : Header distance

                this.PageMargins.Header = Reader.GetDouble();

                break;
            }

            case AscDFH.historyitem_Section_PageMargins_Footer:
            {
                // Double : Footer distance

                this.PageMargins.Footer = Reader.GetDouble();

                break;
            }

            case AscDFH.historyitem_Section_PageNumType_Start:
            {
                // Long : PageNumType.Start

                this.PageNumType.Start = Reader.GetLong();

                break;
            }

            case AscDFH.historyitem_Section_Columns_EqualWidth:
            {
                // Bool : Equal
                this.Columns.EqualWidth = Reader.GetBool();
                break;
            }

            case AscDFH.historyitem_Section_Columns_Space:
            {
                // Double : Space
                this.Columns.Space = Reader.GetDouble();
                break;
            }

            case AscDFH.historyitem_Section_Columns_Num:
            {
                // Long : Num
                this.Columns.Num = Reader.GetLong();
                break;
            }

            case AscDFH.historyitem_Section_Columns_Sep:
            {
                // Bool : Sep
                this.Columns.Sep = Reader.GetBool();
                break;
            }

            case AscDFH.historyitem_Section_Columns_Col:
            {
                // Long : Index
                // Bool : undefined ?
                // false -> 
                //   Variable : CSectionColumn

                var Index = Reader.GetLong();
                
                if ( true === Reader.GetBool() )
                    this.Columns.Cols[Index] = undefined;
                else
                {
                    this.Columns.Cols[Index] = new CSectionColumn();
                    this.Columns.Cols[Index].Read_FromBinary( Reader );
                }

                break;
            }

            case AscDFH.historyitem_Section_Columns_SetCols:
            {
                // Long : Count
                // Array of variable : array of CSectionColumn

                var Count = Reader.GetLong();
                this.Columns.Cols = [];
                for (var Index = 0; Index < Count; ++Index)
                {
                    this.Columns.Cols[Index] = new CSectionColumn();
                    this.Columns.Cols[Index].Read_FromBinary(Reader);
                }
                break;
            }
        }
    },

    Write_ToBinary2 : function(Writer)
    {
        Writer.WriteLong( AscDFH.historyitem_type_Section );

        // String2  : Id
        // String2  : Id LogicDocument
        // Variable : PageSize
        // Variable : PageMargins
        // Byte     : Type
        // Variable : Borders        
        // Колонтитулы не пишем в бинарник, при созданиии класса они всегда null, а TitlePage = false
        // Variable : PageNumType
        // Variable : CSectionColumns

        Writer.WriteString2( "" + this.Id );
        Writer.WriteString2( "" + this.LogicDocument.Get_Id() );
        this.PageSize.Write_ToBinary( Writer );
        this.PageMargins.Write_ToBinary( Writer );
        Writer.WriteByte( this.Type );
        this.Borders.Write_ToBinary( Writer );
        this.PageNumType.Write_ToBinary( Writer );
        this.Columns.Write_ToBinary(Writer);
    },

    Read_FromBinary2 : function(Reader)
    {
        // String2  : Id
        // String2  : Id LogicDocument
        // Variable : PageSize
        // Variable : PageMargins
        // Byte     : Type
        // Variable : Borders
        // Колонтитулы не пишем в бинарник, при созданиии класса они всегда null, а TitlePage = false
        // Variable : PageNumType
        // Variable : CSectionColumns

        this.Id = Reader.GetString2();
        this.LogicDocument = g_oTableId.Get_ById( Reader.GetString2() );
        this.PageSize.Read_FromBinary( Reader );
        this.PageMargins.Read_FromBinary( Reader );
        this.Type = Reader.GetByte();
        this.Borders.Read_FromBinary( Reader );
        this.PageNumType.Read_FromBinary( Reader );
        this.Columns.Read_FromBinary(Reader);
    }
};

function CSectionPageSize()
{
    this.W      = 210;
    this.H      = 297;
    this.Orient = Asc.c_oAscPageOrientation.PagePortrait;
}

CSectionPageSize.prototype =
{
    Write_ToBinary : function(Writer)
    {
        // Double : W
        // Double : H
        // Byte   : Orient

        Writer.WriteDouble( this.W );
        Writer.WriteDouble( this.H );
        Writer.WriteByte( this.Orient );
    },

    Read_FromBinary : function(Reader)
    {
        // Double : W
        // Double : H
        // Byte   : Orient

        this.W      = Reader.GetDouble();
        this.H      = Reader.GetDouble();
        this.Orient = Reader.GetByte();
    }
};

function CSectionPageMargins()
{
    this.Left   = 30; // 3 cm
    this.Top    = 20; // 2 cm
    this.Right  = 15; // 1.5 cm
    this.Bottom = 20; // 2 cm
    
    this.Header = 12.5; // 1.25 cm
    this.Footer = 12.5; // 1.25 cm
}

CSectionPageMargins.prototype =
{
    Write_ToBinary : function(Writer)
    {
        // Double : Left
        // Double : Top
        // Double : Right
        // Double : Bottom
        // Double : Header
        // Double : Footer        

        Writer.WriteDouble( this.Left );
        Writer.WriteDouble( this.Top );
        Writer.WriteDouble( this.Right );
        Writer.WriteDouble( this.Bottom );
        Writer.WriteDouble( this.Header );
        Writer.WriteDouble( this.Footer );
    },

    Read_FromBinary : function(Reader)
    {
        // Double : Left
        // Double : Top
        // Double : Right
        // Double : Bottom
        // Double : Header
        // Double : Footer        

        this.Left   = Reader.GetDouble();
        this.Top    = Reader.GetDouble();
        this.Right  = Reader.GetDouble();
        this.Bottom = Reader.GetDouble();
        this.Header = Reader.GetDouble();
        this.Footer = Reader.GetDouble();
    }
};

function CSectionBorders()
{
    this.Top        = new CDocumentBorder();
    this.Bottom     = new CDocumentBorder();
    this.Left       = new CDocumentBorder();
    this.Right      = new CDocumentBorder();
    
    this.Display    = section_borders_DisplayAllPages;
    this.OffsetFrom = section_borders_OffsetFromPage;
    this.ZOrder     = section_borders_ZOrderFront;
}

CSectionBorders.prototype =
{
    Write_ToBinary : function(Writer)
    {
        // Variable : Left
        // Variable : Top
        // Variable : Right
        // Variable : Bottom
        // Byte     : Display
        // Byte     : OffsetFrom
        // Byte     : ZOrder

        this.Left.Write_ToBinary(Writer);
        this.Top.Write_ToBinary(Writer);
        this.Right.Write_ToBinary(Writer);
        this.Bottom.Write_ToBinary(Writer);
        Writer.WriteByte(this.Display);
        Writer.WriteByte(this.OffsetFrom);
        Writer.WriteByte(this.ZOrder);
    },

    Read_FromBinary : function(Reader)
    {
        // Variable : Left
        // Variable : Top
        // Variable : Right
        // Variable : Bottom
        // Byte     : Display
        // Byte     : OffsetFrom
        // Byte     : ZOrder

        this.Left.Read_FromBinary(Reader);
        this.Top.Read_FromBinary(Reader);
        this.Right.Read_FromBinary(Reader);
        this.Bottom.Read_FromBinary(Reader);

        this.Display    = Reader.GetByte();
        this.OffsetFrom = Reader.GetByte();
        this.ZOrder     = Reader.GetByte();
    }
};

function CSectionPageNumType()
{
    this.Start = -1;
}

CSectionPageNumType.prototype = 
{
    Write_ToBinary : function(Writer)
    {
        // Long : Start
        
        Writer.WriteLong( this.Start );
    },
    
    Read_FromBinary : function(Reader)
    {
        // Long : Start

        this.Start = Reader.GetLong();
    }    
};


function CSectionPageNumInfo(FP, CP, bFirst, bEven, PageNum)
{
    this.FirstPage = FP;
    this.CurPage   = CP;
    this.bFirst    = bFirst;
    this.bEven     = bEven;
    
    this.PageNum   = PageNum;
}

CSectionPageNumInfo.prototype =
{
    Compare : function(Other)
    {
        if ( undefined === Other || null === Other || this.CurPage !== Other.CurPage || this.bFirst !== Other.bFirst || this.bEven !== Other.bEven || this.PageNum !== Other.PageNum )
            return false;
        
        return true;
    }
};

function CSectionColumn()
{
	this.W     = 0;
	this.Space = 0;
}

CSectionColumn.prototype.Write_ToBinary  = function(Writer)
{
	// Double : W
	// Double : Space

	Writer.WriteDouble(this.W);
	Writer.WriteDouble(this.Space);
};
CSectionColumn.prototype.Read_FromBinary = function(Reader)
{
	// Double : W
	// Double : Space

	this.W     = Reader.GetDouble();
	this.Space = Reader.GetDouble();
};

function CSectionColumns(SectPr)
{
	this.SectPr     = SectPr;
	this.EqualWidth = true;
	this.Num        = 1;
	this.Sep        = false;
	this.Space      = 30;

	this.Cols = [];
}

CSectionColumns.prototype.Write_ToBinary  = function(Writer)
{
	// Bool   : Equal
	// Long   : Num
	// Bool   : Sep
	// Double : Space

	// Long   : Количество колонок
	// Variable : Сами колонки

	Writer.WriteBool(this.EqualWidth);
	Writer.WriteLong(this.Num);
	Writer.WriteBool(this.Sep);
	Writer.WriteDouble(this.Space);

	var Count = this.Cols.length;
	Writer.WriteLong(Count);

	for (var Pos = 0; Pos < Count; Pos++)
	{
		this.Cols[Pos].Write_ToBinary(Writer);
	}
};
CSectionColumns.prototype.Read_FromBinary = function(Reader)
{
	// Bool   : Equal
	// Long   : Num
	// Bool   : Sep
	// Double : Space

	// Long   : Количество колонок
	// Variable : Сами колонки

	this.EqualWidth = Reader.GetBool();
	this.Num        = Reader.GetLong();
	this.Sep        = Reader.GetBool();
	this.Space      = Reader.GetDouble();

	var Count = Reader.GetLong();
	this.Cols = [];

	for (var Pos = 0; Pos < Count; Pos++)
	{
		this.Cols[Pos] = new CSectionColumn();
		this.Cols[Pos].Read_FromBinary(Reader);
	}
};
CSectionColumns.prototype.Get_Count       = function()
{
	if (true === this.EqualWidth)
	{
		return this.Num;
	}
	else
	{
		if (this.Cols.length <= 0)
			return 1;

		return this.Cols.length;
	}
};
CSectionColumns.prototype.Get_ColumnWidth = function(ColIndex)
{
	if (true === this.EqualWidth)
	{
		var PageW   = this.SectPr.Get_PageWidth();
		var MarginL = this.SectPr.Get_PageMargin_Left();
		var MarginR = this.SectPr.Get_PageMargin_Right();
		return this.Num > 0 ? (PageW - MarginL - MarginR - this.Space * (this.Num - 1)) / this.Num : (PageW - MarginL - MarginR);
	}
	else
	{
		if (this.Cols.length <= 0)
			return 0;

		ColIndex = Math.max(0, Math.min(this.Cols.length - 1, ColIndex));
		if (ColIndex < 0)
			return 0;

		return this.Cols[ColIndex].W;
	}
};
CSectionColumns.prototype.Get_ColumnSpace = function(ColIndex)
{
	if (true === this.EqualWidth)
	{
		return this.Space;
	}
	else
	{
		if (this.Cols.length <= 0)
			return this.Space;

		ColIndex = Math.max(0, Math.min(this.Cols.length - 1, ColIndex));
		if (ColIndex < 0)
			return this.Space;

		return this.Cols[ColIndex].Space;
	}
};

function CSectionLayoutColumnInfo(X, XLimit)
{
    this.X      = X;
    this.XLimit = XLimit;
    
    this.Pos    = 0;
    this.EndPos = 0;
}

function CSectionLayoutInfo(X, Y, XLimit, YLimit)
{
    this.X       = X;
    this.Y       = Y;
    this.XLimit  = XLimit;
    this.YLimit  = YLimit;
    this.Columns = [];
}

//--------------------------------------------------------export----------------------------------------------------
window['AscCommonWord'] = window['AscCommonWord'] || {};
window['AscCommonWord'].CSectionPr = CSectionPr;