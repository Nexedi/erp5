import Products.ERP5Type
import Products.ERP5
import Products.ERP5.XML
import Products.ERP5.UI
import Products.ERP5.Document
import Products.ERP5Catalog
import Products.ERP5Form
import Products.ERP5SyncML

# Aliases dictionnary for future upgrade
__module_aliases__ = ( ( 'Products.ERP5.ERP5', Products.ERP5.ERP5Site )
                     , ( 'Products.ERP5.XML.SynchronizationTool',
                                                   Products.ERP5SyncML.SynchronizationTool )
                     , ( 'Products.ERP5.XML.CatalogTool', Products.ERP5Catalog.CatalogTool )
                     , ( 'Products.ERP5.XML.Base', Products.ERP5Type.Base )
                     , ( 'Products.ERP5.XML.XMLObject', Products.ERP5Type.XMLObject )
                     , ( 'Products.ERP5.XML.XMLMatrix', Products.ERP5Type.XMLMatrix )
                     , ( 'Products.ERP5.XML.CatalogTool', Products.ERP5Catalog.CatalogTool )
                     , ( 'Products.ERP5.UI.CategoryTool', Products.ERP5.Tool.CategoryTool )
                     , ( 'Products.ERP5.UI.Category', Products.ERP5.Tool.Category )
                     , ( 'Products.ERP5.UI.Form', Products.ERP5Form.Form )
                     , ( 'Products.ERP5.UI.ListBox', Products.ERP5Form.ListBox )
                     , ( 'Products.ERP5.UI.MatrixBox', Products.ERP5Form.MatrixBox )
                     , ( 'Products.ERP5.UI.RelationField', Products.ERP5Form.RelationField )
                     , ( 'Products.ERP5.UI.MultiRelationField', Products.ERP5Form.MultiRelationField )
                     , ( 'Products.ERP5.UI.ImageField', Products.ERP5Form.ImageField )
                     , ( 'Products.ERP5.UI.SelectionTool', Products.ERP5Form.SelectionTool )
                     , ( 'Products.ERP5.Document.Folder', Products.ERP5Type.Document.Folder )
                     , ( 'Products.ERP5.Document.SalesOpportunity', Products.ERP5.Document.SaleOpportunity )
                     , ( 'Products.ERP5.Document.SalesOpportunity.SalesOpportunity', Products.ERP5.Document.SaleOpportunity.SaleOpportunity )
                     )

# Hard wired aliases
Products.ERP5.ERP5 = Products.ERP5.ERP5Site
Products.ERP5.XML.SynchronizationTool = Products.ERP5SyncML.SynchronizationTool
Products.ERP5.Document.Folder = Products.ERP5Type.Document.Folder
Products.ERP5.XML.CatalogTool = Products.ERP5Catalog.CatalogTool
Products.ERP5.XML.Base = Products.ERP5Type.Base
Products.ERP5.XML.XMLObject = Products.ERP5Type.XMLObject
Products.ERP5.XML.XMLMatrix = Products.ERP5Type.XMLMatrix
Products.ERP5.UI.CategoryTool = Products.ERP5.Tool.CategoryTool
Products.ERP5.UI.Category = Products.ERP5.Tool.Category
Products.ERP5.UI.Form = Products.ERP5Form.Form
Products.ERP5.UI.ListBox = Products.ERP5Form.ListBox
Products.ERP5.UI.MatrixBox = Products.ERP5Form.MatrixBox
Products.ERP5.UI.RelationField = Products.ERP5Form.RelationField
Products.ERP5.UI.MultiRelationField = Products.ERP5Form.MultiRelationField
Products.ERP5.UI.ImageField = Products.ERP5Form.ImageField
Products.ERP5.UI.SelectionTool = Products.ERP5Form.SelectionTool
Products.ERP5.Document.SalesOpportunity = Products.ERP5.Document.SaleOpportunity
Products.ERP5.Document.SalesOpportunity.SalesOpportunity = Products.ERP5.Document.SaleOpportunity.SaleOpportunity

